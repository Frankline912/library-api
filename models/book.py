from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.category import Category


class Book(SQLModel, table=True):
    """Book model for the library database"""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    author: str = Field(index=True, min_length=1, max_length=100)
    isbn: str = Field(index=True, unique=True)
    published_year: int = Field(ge=1000, le=datetime.now().year)
    available: bool = Field(default=True)

    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional["Category"] = Relationship(back_populates="books")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BookCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    isbn: str = Field(min_length=10, max_length=13)
    published_year: int = Field(ge=1000, le=datetime.now().year)
    category_id: Optional[int] = None


class BookUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(default=None, min_length=10, max_length=13)
    published_year: Optional[int] = Field(default=None, ge=1000, le=datetime.now().year)
    available: Optional[bool] = None
    category_id: Optional[int] = None