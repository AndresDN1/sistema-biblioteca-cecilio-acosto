from dataclasses import dataclass
from datetime import date


@dataclass
class BookEntity:
    id: int | None
    collection_id: int
    title: str
    author: str
    publisher: str
    isbn: str | None = None
    publication_year: int | None = None
    dewey_code: str | None = None
    is_braille: bool = False
    is_audiobook: bool = False
    classification_system: str = "Dewey"


@dataclass
class ItemEntity:
    id: int | None
    book_id: int
    shelf_location: str
    is_available: bool = True
    entry_date: date | None = None


@dataclass
class InterestEntity:
    id: int | None
    book_id: int
    user_id: int
