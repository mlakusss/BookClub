from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator

STATUSES = ("В планах", "Читаю", "Прочитана")
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=160)
    genre: str = Field(default="Не указан", max_length=80)
    status: str = "В планах"
    added_on: date = Field(default_factory=date.today)
    rating: int | None = Field(default=None, ge=1, le=5)
    notes: str = Field(default="", max_length=3000)

    @field_validator("title", "author")
    @classmethod
    def strip_required(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Поле не может быть пустым")
        return value

    @field_validator("status")
    @classmethod
    def valid_status(cls, value):
        if value not in STATUSES:
            raise ValueError("Недопустимый статус книги")
        return value

class BookUpdate(BookCreate):
    pass

class BookOut(BookCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
