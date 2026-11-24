from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .schemas import BookCreate, BookUpdate, BookOut, STATUSES
from .services import (create_book, list_books, update_book, delete_book,
                       get_statistics, BookNotFoundError, BookValidationError)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="BookClub — учет книг книжного клуба", version="1.0.0",
              description="Веб-система учета книжного фонда и читательского прогресса клуба.")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    with open("app/static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/api/books", response_model=list[BookOut], tags=["Книги"])
def books(search: str = "", status: str = "", genre: str = "", db: Session = Depends(get_db)):
    try:
        return list_books(db, search, status, genre)
    except BookValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/books", response_model=BookOut, status_code=201, tags=["Книги"])
def add_book(data: BookCreate, db: Session = Depends(get_db)):
    return create_book(db, data)

@app.put("/api/books/{book_id}", response_model=BookOut, tags=["Книги"])
def edit_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    try:
        return update_book(db, book_id, data)
    except BookNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.delete("/api/books/{book_id}", status_code=204, tags=["Книги"])
def remove_book(book_id: int, db: Session = Depends(get_db)):
    try:
        delete_book(db, book_id)
    except BookNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.get("/api/statistics", tags=["Статистика"])
def statistics(db: Session = Depends(get_db)):
    return get_statistics(db)

@app.get("/api/genres", tags=["Справочники"])
def genres(db: Session = Depends(get_db)):
    from sqlalchemy import select
    from .models import Book
    return list(db.scalars(select(Book.genre).distinct().order_by(Book.genre)).all())

@app.get("/api/statuses", tags=["Справочники"])
def statuses():
    return list(STATUSES)
