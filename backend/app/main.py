from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session, selectinload

from app.config import ALLOWED_ORIGINS, DEMO_REVIEWER_NAME
from app.database import get_db
from app.models import PortfolioException, ReviewEvent
from app.schemas import (
    ActivityResponse,
    ExceptionCategory,
    ExceptionDetail,
    ExceptionListResponse,
    ExceptionStatus,
    ExceptionSummary,
    EvidenceResponse,
    HealthResponse,
    ReviewStatus,
    StatusUpdateRequest,
    StatusUpdateResponse,
)

app = FastAPI(
    title="OpsDesk Exception API",
    description="Synthetic-data API for the OpsDesk Phase 2 demo.",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "PATCH"],
    allow_headers=["Content-Type"],
)


def to_evidence(record) -> EvidenceResponse:
    return EvidenceResponse(
        quantity=record.quantity,
        value=record.value,
        asOf=record.as_of.strftime("%b %d, %Y").replace(" 0", " "),
        source=record.source,
    )


def to_detail(exception: PortfolioException) -> ExceptionDetail:
    evidence = {record.side: record for record in exception.evidence}
    return ExceptionDetail(
        id=exception.id,
        account=exception.account,
        household=exception.household,
        category=exception.category,
        description=exception.description,
        priority=exception.priority,
        status=exception.status,
        age=exception.age,
        value=exception.display_value,
        rule=exception.rule,
        internal=to_evidence(evidence["internal"]),
        external=to_evidence(evidence["external"]),
        explanation=exception.explanation,
        checklist=exception.checklist,
        activities=[
            ActivityResponse.model_validate(activity)
            for activity in exception.activities
        ],
    )


@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", database="connected")


@app.get("/api/v1/exceptions", response_model=ExceptionListResponse)
def list_exceptions(
    search: str | None = Query(default=None, max_length=100),
    category: ExceptionCategory | None = None,
    status: ExceptionStatus | None = None,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ExceptionListResponse:
    conditions = []
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        conditions.append(
            or_(
                func.lower(PortfolioException.id).like(term),
                func.lower(PortfolioException.account).like(term),
                func.lower(PortfolioException.household).like(term),
                func.lower(PortfolioException.category).like(term),
            )
        )
    if category is not None:
        conditions.append(PortfolioException.category == category.value)
    if status is not None:
        conditions.append(PortfolioException.status == status.value)

    total = db.scalar(
        select(func.count()).select_from(PortfolioException).where(*conditions)
    ) or 0
    exceptions = db.scalars(
        select(PortfolioException)
        .where(*conditions)
        .order_by(PortfolioException.display_order)
        .limit(limit)
        .offset(offset)
    ).all()
    return ExceptionListResponse(
        items=[
            ExceptionSummary(
                id=item.id,
                account=item.account,
                household=item.household,
                category=item.category,
                description=item.description,
                priority=item.priority,
                status=item.status,
                age=item.age,
                value=item.display_value,
            )
            for item in exceptions
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.get("/api/v1/exceptions/{exception_id}", response_model=ExceptionDetail)
def get_exception(
    exception_id: str,
    db: Session = Depends(get_db),
) -> ExceptionDetail:
    exception = db.scalar(
        select(PortfolioException)
        .options(
            selectinload(PortfolioException.evidence),
            selectinload(PortfolioException.activities),
        )
        .where(PortfolioException.id == exception_id)
    )
    if exception is None:
        raise HTTPException(status_code=404, detail="Exception not found")
    return to_detail(exception)


@app.patch(
    "/api/v1/exceptions/{exception_id}/status",
    response_model=StatusUpdateResponse,
)
def update_exception_status(
    exception_id: str,
    request: StatusUpdateRequest,
    db: Session = Depends(get_db),
) -> StatusUpdateResponse:
    exception = db.scalar(
        select(PortfolioException)
        .options(
            selectinload(PortfolioException.evidence),
            selectinload(PortfolioException.activities),
        )
        .where(PortfolioException.id == exception_id)
        .with_for_update()
    )
    if exception is None:
        raise HTTPException(status_code=404, detail="Exception not found")

    previous_status = exception.status
    next_status = request.status.value
    if previous_status != next_status:
        exception.status = next_status
        db.add(
            ReviewEvent(
                exception_id=exception.id,
                event_type="status_changed",
                previous_status=previous_status,
                status=next_status,
                message=f"Marked {next_status.lower()}",
                actor=DEMO_REVIEWER_NAME,
            )
        )
        db.commit()
        db.refresh(exception)
        db.expire(exception, ["activities"])

    return StatusUpdateResponse(item=to_detail(exception))
