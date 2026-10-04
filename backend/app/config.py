import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./opsdesk.db")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
DEMO_REVIEWER_NAME = os.getenv("DEMO_REVIEWER_NAME", "Abdul Kalam")
