"""Shared connection configuration. URL.create safely encodes password characters."""
import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL, make_url


def database_url():
    load_dotenv()
    if os.getenv("DATABASE_URL"):
        return make_url(os.environ["DATABASE_URL"])
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError(
            "Set POSTGRES_PASSWORD or DATABASE_URL in the backend environment"
        )
    return URL.create(
        "postgresql+asyncpg",
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=password,
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "pokeshop_db"),
    )
