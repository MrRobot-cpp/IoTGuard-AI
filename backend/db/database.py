from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def _migrate_schema() -> None:
    """Add columns introduced after the first DB create (SQLite has no auto-migrate)."""
    insp = inspect(engine)
    if "attack_results" not in insp.get_table_names():
        return

    cols = {c["name"] for c in insp.get_columns("attack_results")}
    alters: list[str] = []
    if "blocked" not in cols:
        alters.append(
            "ALTER TABLE attack_results ADD COLUMN blocked BOOLEAN NOT NULL DEFAULT 0"
        )

    if not alters:
        return

    with engine.begin() as conn:
        for stmt in alters:
            conn.execute(text(stmt))


def init_db():
    from db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_schema()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
