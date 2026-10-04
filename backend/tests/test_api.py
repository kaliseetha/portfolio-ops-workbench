from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed_data import seed_cases


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with TestingSession() as session:
        seed_cases(session)

    def override_get_db() -> Generator[Session, None, None]:
        with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_health_and_exception_list(client: TestClient) -> None:
    health = client.get("/health")
    response = client.get("/api/v1/exceptions")

    assert health.status_code == 200
    assert health.json() == {"status": "ok", "database": "connected"}
    assert response.status_code == 200
    assert response.json()["total"] == 10
    assert response.json()["items"][0]["id"] == "EX-20481"


def test_exception_filters_match_queue_search(client: TestClient) -> None:
    response = client.get(
        "/api/v1/exceptions",
        params={
            "search": "morgan",
            "category": "Position mismatch",
            "status": "Open",
        },
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == ["EX-20481"]


def test_detail_includes_evidence_and_seeded_activity(client: TestClient) -> None:
    response = client.get("/api/v1/exceptions/EX-20481")

    assert response.status_code == 200
    assert response.json()["internal"] == {
        "quantity": "240.00",
        "value": "$41,280.00",
        "asOf": "Sep 30, 2026",
        "source": "Portfolio ledger",
    }
    assert response.json()["activities"][0]["message"] == (
        "Exception detected by configured rule"
    )


def test_status_update_persists_event(client: TestClient) -> None:
    body = {"status": "Resolved"}
    first = client.patch("/api/v1/exceptions/EX-20481/status", json=body)
    repeated = client.patch("/api/v1/exceptions/EX-20481/status", json=body)
    second = client.get("/api/v1/exceptions/EX-20481")

    assert first.status_code == 200
    assert first.json()["item"]["status"] == "Resolved"
    event = first.json()["item"]["activities"][0]
    assert event["previous_status"] == "Open"
    assert event["status"] == "Resolved"
    assert event["actor"] == "Abdul Kalam"
    assert len(repeated.json()["item"]["activities"]) == 2
    assert second.json()["status"] == "Resolved"


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        ("/api/v1/exceptions/EX-missing", 404),
        ("/api/v1/exceptions?status=Unknown", 422),
        ("/api/v1/exceptions/EX-20481/status", 422),
    ],
)
def test_invalid_requests_are_rejected(
    client: TestClient,
    path: str,
    expected_status: int,
) -> None:
    response = (
        client.patch(path, json={"status": "Open"})
        if path.endswith("/status")
        else client.get(path)
    )

    assert response.status_code == expected_status
