"""Load normalized data into the database."""
from __future__ import annotations

from typing import Iterable

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings


def get_engine():
    settings = get_settings()
    return create_engine(settings.db_url)


def init_db() -> None:
    """Create database tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def load_objects(objs: Iterable[SQLModel]) -> None:
    """Persist SQLModel objects to the database."""
    engine = get_engine()
    with Session(engine) as session:
        for obj in objs:
            session.add(obj)
        session.commit()

