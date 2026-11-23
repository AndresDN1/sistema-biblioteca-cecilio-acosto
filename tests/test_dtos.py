import pytest

from src.dtos.core_dtos import LoginDTO, UserRegistrationDTO, VisitorLogDTO
from src.dtos.inventory_dtos import BookDTO, BookSearchDTO, ItemDTO


def test_user_registration_dto_success():
    payload = {
        "username": "usuario_valido",
        "password": "passwordSeguro123",
        "full_name": "Nombre de Prueba",
    }
    dto = UserRegistrationDTO.from_dict(payload)
    assert dto.username == "usuario_valido"
    assert dto.full_name == "Nombre de Prueba"


def test_user_registration_dto_invalid_username_length():
    with pytest.raises(
        ValueError, match="El nombre de usuario debe tener entre 3 y 20 caracteres"
    ):
        UserRegistrationDTO.from_dict({
            "username": "ab",
            "password": "passwordSeguro123",
            "full_name": "Nombre",
        })


def test_user_registration_dto_invalid_username_characters():
    with pytest.raises(
        ValueError, match="solo puede contener letras, números y guiones bajos"
    ):
        UserRegistrationDTO.from_dict({
            "username": "user-invalid!",
            "password": "passwordSeguro123",
            "full_name": "Nombre",
        })


def test_user_registration_dto_short_password():
    with pytest.raises(
        ValueError, match="La contraseña debe tener entre 8 y 128 caracteres"
    ):
        UserRegistrationDTO.from_dict({
            "username": "usuario_valido",
            "password": "123",
            "full_name": "Nombre",
        })


def test_user_registration_dto_missing_full_name():
    with pytest.raises(ValueError, match="El nombre completo es requerido"):
        UserRegistrationDTO.from_dict({
            "username": "usuario_valido",
            "password": "passwordSeguro123",
            "full_name": "",
        })


def test_login_dto_validation():
    with pytest.raises(ValueError, match="Nombre de usuario requerido"):
        LoginDTO.from_dict({"username": "", "password": "123"})

    with pytest.raises(ValueError, match="Contraseña requerida"):
        LoginDTO.from_dict({"username": "user", "password": ""})


def test_visitor_log_dto_validation():
    valid = VisitorLogDTO.from_dict({
        "visitor_id": "V-12345678",
        "visitor_name": "Juan Perez",
        "contact_info": "juan@test.com",
    })
    assert valid.visitor_id == "V-12345678"
    assert valid.contact_info == "juan@test.com"

    with pytest.raises(ValueError, match="Identificación del visitante requerida"):
        VisitorLogDTO.from_dict({"visitor_id": "", "visitor_name": "Juan"})

    with pytest.raises(ValueError, match="Nombre del visitante requerido"):
        VisitorLogDTO.from_dict({"visitor_id": "V-1", "visitor_name": ""})


def test_book_dto_validation():
    valid_data = {
        "title": "Libro de Prueba",
        "author": "Autor de Prueba",
        "publisher": "Editorial Prueba",
        "publication_year": "2024",
        "is_braille": "true",
    }
    dto = BookDTO.from_dict(valid_data)
    assert dto.title == "Libro de Prueba"
    assert dto.publication_year == 2024
    assert dto.is_braille is True

    with pytest.raises(ValueError, match="El título es obligatorio"):
        BookDTO.from_dict({"title": "", "author": "A", "publisher": "P"})

    with pytest.raises(ValueError, match="El autor es obligatorio"):
        BookDTO.from_dict({"title": "T", "author": "", "publisher": "P"})

    with pytest.raises(ValueError, match="La editorial es obligatoria"):
        BookDTO.from_dict({"title": "T", "author": "A", "publisher": ""})

    with pytest.raises(
        ValueError, match="El año de publicación debe ser un número entero válido"
    ):
        BookDTO.from_dict({
            "title": "T",
            "author": "A",
            "publisher": "P",
            "publication_year": "no_es_anio",
        })


def test_book_search_dto_clean():
    dto = BookSearchDTO.from_dict({
        "title": "  Cien Años  ",
        "author": "",
        "publication_year_from": "1980",
        "is_braille": "true",
        "is_audiobook": "0",
    })
    assert dto.title == "Cien Años"
    assert dto.author is None
    assert dto.publication_year_from == 1980
    assert dto.is_braille is True
    assert dto.is_audiobook is False


def test_item_dto_validation():
    dto = ItemDTO.from_dict({"shelf_location": "Estante A-1", "is_available": True})
    assert dto.shelf_location == "Estante A-1"
    assert dto.is_available is True

    with pytest.raises(ValueError, match="La ubicación en estantería es obligatoria"):
        ItemDTO.from_dict({"shelf_location": "  "})
