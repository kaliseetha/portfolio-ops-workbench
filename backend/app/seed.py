from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import PortfolioException
from app.seed_data import seed_cases


def main() -> None:
    with SessionLocal() as session:
        seed_cases(session)
        count = session.scalar(select(func.count()).select_from(PortfolioException))
        print(f"Seeded synthetic exception cases (total now: {count or 0}).")


if __name__ == "__main__":
    main()
