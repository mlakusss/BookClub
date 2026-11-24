from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .models import Book
from .schemas import BookCreate, BookUpdate, STATUSES

class BookClubError(Exception):
    """Базовая ошибка предметной области."""
class BookNotFoundError(BookClubError):
    pass
class BookValidationError(BookClubError):
    pass

def create_book(db: Session, data: BookCreate) -> Book:
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

def list_books(db: Session, search: str = "", status: str = "", genre: str = ""):
    stmt = select(Book)
    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where((Book.title.ilike(term)) | (Book.author.ilike(term)))
    if status:
        if status not in STATUSES:
            raise BookValidationError("Неизвестный статус")
        stmt = stmt.where(Book.status == status)
    if genre:
        stmt = stmt.where(Book.genre == genre)
    return list(db.scalars(stmt.order_by(Book.added_on.desc(), Book.id.desc())).all())

def get_book(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if not book:
        raise BookNotFoundError(f"Книга с ID {book_id} не найдена")
    return book

def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    book = get_book(db, book_id)
    for key, value in data.model_dump().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

def delete_book(db: Session, book_id: int) -> None:
    book = get_book(db, book_id)
    db.delete(book)
    db.commit()

def get_statistics(db: Session):
    total = db.scalar(select(func.count(Book.id))) or 0
    read = db.scalar(select(func.count(Book.id)).where(Book.status == "Прочитана")) or 0
    reading = db.scalar(select(func.count(Book.id)).where(Book.status == "Читаю")) or 0
    planned = db.scalar(select(func.count(Book.id)).where(Book.status == "В планах")) or 0
    avg = db.scalar(select(func.avg(Book.rating)).where(Book.rating.is_not(None)))
    return {"total": total, "read": read, "reading": reading, "planned": planned,
            "average_rating": round(float(avg), 2) if avg is not None else None}
