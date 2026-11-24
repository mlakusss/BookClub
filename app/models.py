from datetime import date
from sqlalchemy import String, Integer, Date, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Book(Base):
    __tablename__ = "books"
    __table_args__ = (CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="ck_book_rating"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(80), nullable=False, default="Не указан")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="В планах")
    added_on: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
