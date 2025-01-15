
from typing import TypeVar, Optional, Type
from shophive_packages import db

T = TypeVar('T')


def get_by_id(model: Type[T], id: int) -> Optional[T]:
    """Get model instance by ID using modern SQLAlchemy method."""
    return db.session.get(model, id)
