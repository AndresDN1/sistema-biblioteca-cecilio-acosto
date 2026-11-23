from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass
class BookDTO:
    collection_id: int
    title: str
    author: str
    publisher: str
    isbn: str | None = None
    publication_year: int | None = None
    dewey_code: str | None = None
    is_braille: bool = False
    is_audiobook: bool = False
    classification_system: str = "DEWEY"

    @classmethod
    def from_dict(cls, data: dict) -> "BookDTO":
        title = data.get("title")
        author = data.get("author")
        publisher = data.get("publisher")

        if not title or not str(title).strip():
            raise ValueError("El título es obligatorio.")
        if not author or not str(author).strip():
            raise ValueError("El autor es obligatorio.")
        if not publisher or not str(publisher).strip():
            raise ValueError("La editorial es obligatoria.")

        isbn_val = data.get("isbn")
        isbn = (
            isbn_val.strip()
            if isbn_val and isinstance(isbn_val, str) and isbn_val.strip()
            else None
        )

        year_val = data.get("publication_year")
        publication_year = None
        if year_val is not None and str(year_val).strip():
            try:
                publication_year = int(year_val)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    "El año de publicación debe ser un número entero válido."
                ) from e

        dewey_val = data.get("dewey_code")
        dewey_code = (
            dewey_val.strip()
            if dewey_val and isinstance(dewey_val, str) and dewey_val.strip()
            else None
        )

        collection_val = data.get("collection_id", 1)
        try:
            collection_id = int(collection_val)
        except (ValueError, TypeError):
            collection_id = 1

        is_braille = bool(data.get("is_braille", False))
        is_audiobook = bool(data.get("is_audiobook", False))
        classification_system = data.get("classification_system", "DEWEY")

        return cls(
            collection_id=collection_id,
            title=str(title).strip(),
            author=str(author).strip(),
            publisher=str(publisher).strip(),
            isbn=isbn,
            publication_year=publication_year,
            dewey_code=dewey_code,
            is_braille=is_braille,
            is_audiobook=is_audiobook,
            classification_system=classification_system,
        )


@dataclass
class BookSearchDTO:
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    isbn: str | None = None
    dewey_code: str | None = None
    publication_year_from: int | None = None
    is_braille: bool | None = None
    is_audiobook: bool | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "BookSearchDTO":
        def clean_str(key: str) -> str | None:
            val = data.get(key)
            if val is not None and isinstance(val, str) and val.strip() != "":
                return val.strip()
            return None

        def parse_bool(key: str) -> bool | None:
            val = data.get(key)
            if val is None or val == "":
                return None
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.strip().lower() in ("true", "1", "on", "yes")
            return None

        year_val = data.get("publication_year_from") or data.get("publication_year")
        publication_year_from = None
        if year_val is not None and str(year_val).strip() != "":
            try:
                publication_year_from = int(year_val)
            except (ValueError, TypeError):
                publication_year_from = None

        return cls(
            title=clean_str("title"),
            author=clean_str("author"),
            publisher=clean_str("publisher"),
            isbn=clean_str("isbn"),
            dewey_code=clean_str("dewey_code"),
            publication_year_from=publication_year_from,
            is_braille=parse_bool("is_braille"),
            is_audiobook=parse_bool("is_audiobook"),
        )


@dataclass
class ItemDTO:
    shelf_location: str
    is_available: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "ItemDTO":
        shelf_location = data.get("shelf_location")
        if not shelf_location or not str(shelf_location).strip():
            raise ValueError("La ubicación en estantería es obligatoria.")

        is_available = bool(data.get("is_available", True))
        return cls(
            shelf_location=str(shelf_location).strip(),
            is_available=is_available,
        )


@dataclass
class CreateCopyDTO:
    shelf_location: str
    is_available: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CreateCopyDTO":
        shelf_location = data.get("shelf_location")
        if not shelf_location or not str(shelf_location).strip():
            raise ValueError("La ubicación en estantería es obligatoria.")

        is_available = bool(data.get("is_available", True))
        return cls(
            shelf_location=str(shelf_location).strip(),
            is_available=is_available,
        )
