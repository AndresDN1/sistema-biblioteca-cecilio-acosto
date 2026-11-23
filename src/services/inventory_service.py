from src.contracts.inventory_contracts import IBookDAO, IInterestDAO, IItemDAO
from src.dtos.inventory_dtos import BookDTO, BookSearchDTO, ItemDTO
from src.entities.inventory_entities import BookEntity, ItemEntity
from src.exceptions.inventory_exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    ItemNotFoundError,
)


class InventoryService:
    def __init__(
        self,
        book_dao: IBookDAO,
        item_dao: IItemDAO,
        interest_dao: IInterestDAO,
    ):
        self.book_dao = book_dao
        self.item_dao = item_dao
        self.interest_dao = interest_dao

    def create_book(self, dto: BookDTO) -> BookEntity:
        if dto.isbn and dto.isbn.strip():
            existing = self.book_dao.get_by_isbn(dto.isbn)
            if existing is not None:
                raise BookAlreadyExistsError(
                    f"El libro con el ISBN '{dto.isbn}' ya existe."
                )

        book = BookEntity(
            id=None,
            collection_id=dto.collection_id,
            title=dto.title,
            author=dto.author,
            publisher=dto.publisher,
            isbn=dto.isbn,
            publication_year=dto.publication_year,
            dewey_code=dto.dewey_code,
            is_braille=dto.is_braille,
            is_audiobook=dto.is_audiobook,
            classification_system=dto.classification_system,
        )
        return self.book_dao.save(book)

    def update_book(self, book_id: int, dto: BookDTO) -> BookEntity:
        book = self.book_dao.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Libro ID {book_id} no encontrado.")

        if dto.isbn and dto.isbn.strip() and dto.isbn != book.isbn:
            existing = self.book_dao.get_by_isbn(dto.isbn)
            if existing is not None:
                raise BookAlreadyExistsError(
                    f"El libro con el ISBN '{dto.isbn}' ya existe."
                )

        book.collection_id = dto.collection_id
        book.title = dto.title
        book.author = dto.author
        book.publisher = dto.publisher
        book.isbn = dto.isbn
        book.publication_year = dto.publication_year
        book.dewey_code = dto.dewey_code
        book.is_braille = dto.is_braille
        book.is_audiobook = dto.is_audiobook
        book.classification_system = dto.classification_system

        return self.book_dao.save(book)

    def delete_book(self, book_id: int) -> bool:
        success = self.book_dao.delete(book_id)
        if not success:
            raise BookNotFoundError(f"Libro ID {book_id} no encontrado.")
        return True

    def get_book_details(self, book_id: int, user_id: int | None = None) -> dict:
        book = self.book_dao.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Libro ID {book_id} no encontrado.")

        items = self.item_dao.get_by_book_id(book_id)
        is_interested = False
        if user_id:
            is_interested = self.interest_dao.is_interested(book_id, user_id)

        is_accessible = len(items) > 0
        primary_shelf_location = items[0].shelf_location if is_accessible else None

        return {
            "book": book,
            "items": items,
            "is_interested": is_interested,
            "is_accessible": is_accessible,
            "primary_shelf_location": primary_shelf_location,
        }

    def search_books(self, dto: BookSearchDTO) -> list[BookEntity]:
        return self.book_dao.search(
            title=dto.title,
            author=dto.author,
            publisher=dto.publisher,
            isbn=dto.isbn,
            dewey_code=dto.dewey_code,
            publication_year_from=dto.publication_year_from,
            is_braille=dto.is_braille,
            is_audiobook=dto.is_audiobook,
        )

    def add_item(self, book_id: int, dto: ItemDTO) -> ItemEntity:
        book = self.book_dao.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Libro ID {book_id} no encontrado.")

        item = ItemEntity(
            id=None,
            book_id=book_id,
            shelf_location=dto.shelf_location,
            is_available=dto.is_available,
        )
        return self.item_dao.save(item)

    def set_item_unavailable(self, item_id: int) -> bool:
        item = self.item_dao.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(f"Ejemplar ID {item_id} no encontrado.")

        return self.item_dao.set_availability(item_id, is_available=False)

    def toggle_interest(self, book_id: int, user_id: int) -> bool:
        book = self.book_dao.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Libro ID {book_id} no encontrado.")

        if self.interest_dao.is_interested(book_id, user_id):
            self.interest_dao.remove_interest(book_id, user_id)
            return False
        else:
            self.interest_dao.add_interest(book_id, user_id)
            return True

    def get_user_interested_books(self, user_id: int) -> list[BookEntity]:
        return self.interest_dao.get_user_interested_books(user_id)

    def remove_item(self, item_id: int) -> bool:
        success = self.item_dao.delete(item_id)
        if not success:
            raise ItemNotFoundError(f"Ejemplar ID {item_id} no encontrado.")
        return True
