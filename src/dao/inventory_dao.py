from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.contracts.inventory_contracts import IBookDAO, IInterestDAO, IItemDAO
from src.entities.inventory_entities import BookEntity, InterestEntity, ItemEntity
from src.extensions import db
from src.models.inventory_models import BookModel, InterestModel, ItemModel


class PostgresBookDAO(IBookDAO):
    def _to_entity(self, model: BookModel) -> BookEntity:
        return BookEntity(
            id=model.id,
            collection_id=model.collection_id,
            isbn=model.isbn,
            title=model.title,
            author=model.author,
            publisher=model.publisher,
            publication_year=model.publication_year,
            dewey_code=model.dewey_code,
            is_braille=model.is_braille,
            is_audiobook=model.is_audiobook,
            classification_system=model.classification_system,
        )

    def save(self, book: BookEntity) -> BookEntity:
        try:
            if book.id is None:
                model = BookModel()
            else:
                stmt = select(BookModel).where(BookModel.id == book.id)
                model = db.session.execute(stmt).scalars().first()
                if model is None:
                    raise KeyError(f"Libro con ID {book.id} no encontrado.")

            model.collection_id = book.collection_id
            model.isbn = book.isbn
            model.title = book.title
            model.author = book.author
            model.publisher = book.publisher
            model.publication_year = book.publication_year
            model.dewey_code = book.dewey_code
            model.is_braille = book.is_braille
            model.is_audiobook = book.is_audiobook
            model.classification_system = book.classification_system

            if book.id is None:
                db.session.add(model)

            db.session.flush()
            book.id = model.id
            db.session.commit()
            return book
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def get_by_id(self, book_id: int) -> BookEntity | None:
        stmt = select(BookModel).where(BookModel.id == book_id)
        model = db.session.execute(stmt).scalars().first()
        return self._to_entity(model) if model else None

    def get_by_isbn(self, isbn: str) -> BookEntity | None:
        if not isbn or not isbn.strip():
            return None
        stmt = select(BookModel).where(BookModel.isbn == isbn.strip())
        model = db.session.execute(stmt).scalars().first()
        return self._to_entity(model) if model else None

    def delete(self, book_id: int) -> bool:
        stmt = select(BookModel).where(BookModel.id == book_id)
        model = db.session.execute(stmt).scalars().first()
        if model is None:
            return False
        try:
            db.session.delete(model)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            raise

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
        stmt = select(BookModel)

        if title and isinstance(title, str) and title.strip():
            stmt = stmt.where(BookModel.title.ilike(f"%{title.strip()}%"))
        if author and isinstance(author, str) and author.strip():
            stmt = stmt.where(BookModel.author.ilike(f"%{author.strip()}%"))
        if publisher and isinstance(publisher, str) and publisher.strip():
            stmt = stmt.where(BookModel.publisher.ilike(f"%{publisher.strip()}%"))
        if isbn and isinstance(isbn, str) and isbn.strip():
            stmt = stmt.where(BookModel.isbn.ilike(f"%{isbn.strip()}%"))
        if dewey_code and isinstance(dewey_code, str) and dewey_code.strip():
            stmt = stmt.where(BookModel.dewey_code.ilike(f"%{dewey_code.strip()}%"))

        if publication_year_from is not None:
            stmt = stmt.where(BookModel.publication_year >= publication_year_from)

        if is_braille is True:
            stmt = stmt.where(BookModel.is_braille.is_(True))
        if is_audiobook is True:
            stmt = stmt.where(BookModel.is_audiobook.is_(True))

        models = db.session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in models]


class PostgresItemDAO(IItemDAO):
    def _to_entity(self, model: ItemModel) -> ItemEntity:
        return ItemEntity(
            id=model.id,
            book_id=model.book_id,
            shelf_location=model.shelf_location,
            is_available=model.is_available,
            entry_date=model.entry_date,
        )

    def save(self, item: ItemEntity) -> ItemEntity:
        try:
            if item.id is None:
                model = ItemModel()
            else:
                stmt = select(ItemModel).where(ItemModel.id == item.id)
                model = db.session.execute(stmt).scalars().first()
                if model is None:
                    raise KeyError(f"Ejemplar con ID {item.id} no encontrado.")

            model.book_id = item.book_id
            model.shelf_location = item.shelf_location
            model.is_available = item.is_available

            if item.id is None:
                db.session.add(model)

            db.session.flush()
            item.id = model.id
            item.entry_date = model.entry_date
            db.session.commit()
            return item
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def get_by_id(self, item_id: int) -> ItemEntity | None:
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        model = db.session.execute(stmt).scalars().first()
        return self._to_entity(model) if model else None

    def get_by_book_id(self, book_id: int) -> list[ItemEntity]:
        stmt = select(ItemModel).where(ItemModel.book_id == book_id)
        models = db.session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in models]

    def set_availability(self, item_id: int, is_available: bool) -> bool:
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        model = db.session.execute(stmt).scalars().first()
        if model is None:
            return False
        model.is_available = is_available
        try:
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def delete(self, item_id: int) -> bool:
        try:
            stmt = select(ItemModel).where(ItemModel.id == item_id)
            model = db.session.execute(stmt).scalars().first()
            if model is None:
                return False
            db.session.delete(model)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            raise


class PostgresInterestDAO(IInterestDAO):
    def add_interest(self, book_id: int, user_id: int) -> InterestEntity:
        try:
            model = InterestModel()
            model.book_id = book_id
            model.user_id = user_id

            db.session.add(model)
            db.session.flush()
            entity = InterestEntity(id=model.id, book_id=book_id, user_id=user_id)
            db.session.commit()
            return entity
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def remove_interest(self, book_id: int, user_id: int) -> bool:
        try:
            stmt = select(InterestModel).where(
                InterestModel.book_id == book_id,
                InterestModel.user_id == user_id,
            )
            model = db.session.execute(stmt).scalars().first()
            if model is None:
                return False

            db.session.delete(model)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def is_interested(self, book_id: int, user_id: int) -> bool:
        stmt = select(InterestModel).where(
            InterestModel.book_id == book_id,
            InterestModel.user_id == user_id,
        )
        model = db.session.execute(stmt).scalars().first()
        return model is not None

    def get_user_interested_books(self, user_id: int) -> list[BookEntity]:
        stmt = (
            select(BookModel)
            .join(InterestModel, BookModel.id == InterestModel.book_id)
            .where(InterestModel.user_id == user_id)
        )
        models = db.session.execute(stmt).scalars().all()

        book_dao = PostgresBookDAO()
        return [book_dao._to_entity(m) for m in models]
