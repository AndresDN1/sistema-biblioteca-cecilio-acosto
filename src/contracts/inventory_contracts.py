from abc import ABC, abstractmethod

from src.entities.inventory_entities import BookEntity, InterestEntity, ItemEntity


class IBookDAO(ABC):
    @abstractmethod
    def save(self, book: BookEntity) -> BookEntity:
        pass

    @abstractmethod
    def get_by_id(self, book_id: int) -> BookEntity | None:
        pass

    @abstractmethod
    def get_by_isbn(self, isbn: str) -> BookEntity | None:
        pass

    @abstractmethod
    def delete(self, book_id: int) -> bool:
        pass

    @abstractmethod
    def search(
        self,
        title: str | None = None,
        author: str | None = None,
        publisher: str | None = None,
        isbn: str | None = None,
        dewey_code: str | None = None,
        publication_year_from: int | None = None,
        is_braille: bool | None = None,
        is_audiobook: bool | None = None,
    ) -> list[BookEntity]:
        pass


class IItemDAO(ABC):
    @abstractmethod
    def save(self, item: ItemEntity) -> ItemEntity:
        pass

    @abstractmethod
    def get_by_id(self, item_id: int) -> ItemEntity | None:
        pass

    @abstractmethod
    def get_by_book_id(self, book_id: int) -> list[ItemEntity]:
        pass

    @abstractmethod
    def set_availability(self, item_id: int, is_available: bool) -> bool:
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        pass


class IInterestDAO(ABC):
    @abstractmethod
    def add_interest(self, book_id: int, user_id: int) -> InterestEntity:
        pass

    @abstractmethod
    def remove_interest(self, book_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def is_interested(self, book_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_user_interested_books(self, user_id: int) -> list[BookEntity]:
        pass
