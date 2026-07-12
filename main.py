from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, select
from typing import List, Optional
from datetime import datetime

from database.session import engine, get_session
from models.book import Book, BookCreate, BookUpdate
from models.category import Category

# Create database tables
SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="Library API",
    description="A simple library management API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Welcome to the Library API"}


# -----------------------------
# CATEGORY ENDPOINT
# -----------------------------
@app.post("/categories", response_model=Category)
def create_category(
    name: str,
    session: Session = Depends(get_session)
):
    """Create a new category"""

    category = Category(name=name)

    session.add(category)
    session.commit()
    session.refresh(category)

    return category


# -----------------------------
# CREATE BOOK
# -----------------------------
@app.post("/books", response_model=Book)
def create_book(
    book: BookCreate,
    session: Session = Depends(get_session)
):
    """Create a new book"""

    # Check whether the category exists (if one was supplied)
    if book.category_id is not None:
        category = session.get(Category, book.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    db_book = Book(**book.model_dump())

    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    return db_book


# -----------------------------
# LIST BOOKS
# -----------------------------
@app.get("/books", response_model=List[Book])
def list_books(
    skip: int = 0,
    limit: int = 10,
    available: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """List all books"""

    query = select(Book)

    if available is not None:
        query = query.where(Book.available == available)

    return session.exec(query.offset(skip).limit(limit)).all()


# -----------------------------
# SEARCH BOOKS
# -----------------------------
@app.get("/books/search", response_model=List[Book])
def search_books(
    author: Optional[str] = None,
    title: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Search books by author and/or title"""

    query = select(Book)

    if author:
        query = query.where(Book.author.contains(author))

    if title:
        query = query.where(Book.title.contains(title))

    return session.exec(query).all()


# -----------------------------
# GET BOOK BY ID
# -----------------------------
@app.get("/books/{book_id}", response_model=Book)
def get_book(
    book_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific book"""

    book = session.get(Book, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# -----------------------------
# UPDATE BOOK
# -----------------------------
@app.patch("/books/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session)
):
    """Update a book"""

    book = session.get(Book, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.model_dump(exclude_unset=True)

    # Check whether the new category exists
    if "category_id" in update_data and update_data["category_id"] is not None:
        category = session.get(Category, update_data["category_id"])
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    for field, value in update_data.items():
        setattr(book, field, value)

    book.updated_at = datetime.utcnow()

    session.add(book)
    session.commit()
    session.refresh(book)

    return book