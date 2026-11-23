import secrets
from unittest.mock import MagicMock

import pytest
from flask import Flask

from src.contracts.core_contracts import IUserDAO, IVisitorLogDAO
from src.contracts.inventory_contracts import IBookDAO, IInterestDAO, IItemDAO
from src.services.core_service import CoreService
from src.services.inventory_service import InventoryService


@pytest.fixture
def mock_user_dao():
    return MagicMock(spec=IUserDAO)


@pytest.fixture
def mock_visitor_log_dao():
    return MagicMock(spec=IVisitorLogDAO)


@pytest.fixture
def mock_book_dao():
    return MagicMock(spec=IBookDAO)


@pytest.fixture
def mock_item_dao():
    return MagicMock(spec=IItemDAO)


@pytest.fixture
def mock_interest_dao():
    return MagicMock(spec=IInterestDAO)


@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    with app.test_request_context():
        yield app


@pytest.fixture
def core_service(mock_user_dao, mock_visitor_log_dao):
    return CoreService(
        user_dao=mock_user_dao,
        visitor_log_dao=mock_visitor_log_dao,
    )


@pytest.fixture
def inventory_service(mock_book_dao, mock_item_dao, mock_interest_dao):
    return InventoryService(
        book_dao=mock_book_dao,
        item_dao=mock_item_dao,
        interest_dao=mock_interest_dao,
    )
