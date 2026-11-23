import pytest

from src.dtos.inventory_dtos import BookDTO, ItemDTO
from src.entities.inventory_entities import BookEntity, ItemEntity
from src.exceptions.inventory_exceptions import (
    BookAlreadyExistsError,
    BookNotFoundError,
    ItemNotFoundError,
)


def test_create_book_success(inventory_service, mock_book_dao):
    mock_book_dao.get_by_isbn.return_value = None

    def fake_save(book):
        book.id = 100
        return book

    mock_book_dao.save.side_effect = fake_save

    dto = BookDTO(
        collection_id=1,
        title="Libro Nuevo",
        author="Autor",
        publisher="Editorial",
        isbn="978-000-111-2",
    )
    created = inventory_service.create_book(dto)

    assert created.id == 100
    assert created.title == "Libro Nuevo"


def test_create_book_duplicate_isbn(inventory_service, mock_book_dao):
    existing = BookEntity(1, 1, "Viejo", "A", "E", isbn="978-000-111-2")
    mock_book_dao.get_by_isbn.return_value = existing

    dto = BookDTO(
        collection_id=1,
        title="Libro Nuevo",
        author="Autor",
        publisher="Editorial",
        isbn="978-000-111-2",
    )
    with pytest.raises(BookAlreadyExistsError, match="ya existe"):
        inventory_service.create_book(dto)


def test_update_book_success(inventory_service, mock_book_dao):
    book = BookEntity(5, 1, "Titulo Viejo", "Autor", "Editorial", isbn="111")
    mock_book_dao.get_by_id.return_value = book
    mock_book_dao.get_by_isbn.return_value = None
    mock_book_dao.save.side_effect = lambda b: b

    dto = BookDTO(
        collection_id=1,
        title="Titulo Editado",
        author="Autor",
        publisher="Editorial",
        isbn="222",
    )
    updated = inventory_service.update_book(5, dto)

    assert updated.title == "Titulo Editado"
    assert updated.isbn == "222"


def test_update_book_not_found(inventory_service, mock_book_dao):
    mock_book_dao.get_by_id.return_value = None
    dto = BookDTO(1, "T", "A", "E")

    with pytest.raises(BookNotFoundError):
        inventory_service.update_book(999, dto)


def test_delete_book_success(inventory_service, mock_book_dao):
    mock_book_dao.delete.return_value = True
    assert inventory_service.delete_book(10) is True


def test_delete_book_not_found(inventory_service, mock_book_dao):
    mock_book_dao.delete.return_value = False
    with pytest.raises(BookNotFoundError):
        inventory_service.delete_book(999)


def test_get_book_details_with_user(
    inventory_service, mock_book_dao, mock_item_dao, mock_interest_dao
):
    book = BookEntity(1, 1, "Titulo", "Autor", "Editorial")
    items = [
        ItemEntity(10, 1, "Estante 1", is_available=True),
        ItemEntity(11, 1, "Estante 2", is_available=False),
    ]
    mock_book_dao.get_by_id.return_value = book
    mock_item_dao.get_by_book_id.return_value = items
    mock_interest_dao.is_interested.return_value = True

    details = inventory_service.get_book_details(book_id=1, user_id=42)

    assert details["book"] == book
    assert len(details["items"]) == 2
    assert details["is_interested"] is True
    assert details["is_accessible"] is True
    assert details["primary_shelf_location"] == "Estante 1"


def test_get_book_details_not_found(inventory_service, mock_book_dao):
    mock_book_dao.get_by_id.return_value = None
    with pytest.raises(BookNotFoundError):
        inventory_service.get_book_details(404)


def test_toggle_interest(inventory_service, mock_book_dao, mock_interest_dao):
    mock_book_dao.get_by_id.return_value = BookEntity(1, 1, "T", "A", "E")

    mock_interest_dao.is_interested.return_value = True
    assert inventory_service.toggle_interest(1, 10) is False
    mock_interest_dao.remove_interest.assert_called_once_with(1, 10)

    mock_interest_dao.is_interested.return_value = False
    assert inventory_service.toggle_interest(1, 10) is True
    mock_interest_dao.add_interest.assert_called_once_with(1, 10)


def test_add_item_success(inventory_service, mock_book_dao, mock_item_dao):
    mock_book_dao.get_by_id.return_value = BookEntity(1, 1, "T", "A", "E")
    mock_item_dao.save.side_effect = lambda it: it

    dto = ItemDTO("Estante C-1", is_available=True)
    item = inventory_service.add_item(1, dto)

    assert item.shelf_location == "Estante C-1"
    assert item.book_id == 1


def test_remove_item_success(inventory_service, mock_item_dao):
    mock_item_dao.delete.return_value = True
    assert inventory_service.remove_item(7) is True


def test_remove_item_not_found(inventory_service, mock_item_dao):
    mock_item_dao.delete.return_value = False
    with pytest.raises(ItemNotFoundError):
        inventory_service.remove_item(777)
