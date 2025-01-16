from typing import Protocol, Type, TypeVar, runtime_checkable, Any, List
from flask_sqlalchemy.query import Query as FSQuery
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Mapped
from sqlalchemy.orm.relationships import RelationshipProperty


@runtime_checkable
class ModelProtocol(Protocol):
    """Protocol for SQLAlchemy models"""
    query: 'BaseQuery'
    id: Mapped[int]
    username: Mapped[str]
    email: Mapped[str]


class ModelMetaclass(DeclarativeMeta):
    """
    Metaclass for SQLAlchemy models that implements ModelProtocol
    """
    pass


class BaseQuery(FSQuery):
    """Type stub for Flask-SQLAlchemy Query class"""
    def get_or_404(
        self, ident: Any, description: str | None = None
    ) -> Any: ...
    def first_or_404(self, description: str | None = None) -> Any: ...


T = TypeVar('T', bound=ModelProtocol)
SQLAlchemyModel = Type[T]

# Add type aliases for relationships
RelationshipList = List[Any]
Relationship = RelationshipProperty[Any]
