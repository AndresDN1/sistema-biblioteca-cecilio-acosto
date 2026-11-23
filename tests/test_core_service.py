from datetime import datetime

import pytest
from flask import session

from src.dtos.core_dtos import LoginDTO, UserRegistrationDTO, VisitorLogDTO
from src.entities.core_entities import UserEntity, VisitorLogEntity
from src.exceptions.core_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    VisitorLogCreationError,
)
from src.utils.security import hash_password


def test_register_user_success(app_context, core_service, mock_user_dao):
    mock_user_dao.get_by_username.return_value = None

    def fake_save(user):
        user.id = 10
        return user

    mock_user_dao.save.side_effect = fake_save

    dto = UserRegistrationDTO("nuevo_usuario", "passwordSeguro1", "Juan Perez")
    created = core_service.register_user(dto)

    assert created.id == 10
    assert created.username == "nuevo_usuario"
    assert session.get("user_id") == 10
    assert session.get("role") == "USER"


def test_register_user_conflict(app_context, core_service, mock_user_dao):
    existing = UserEntity(1, "existente", "hash", "Juan")
    mock_user_dao.get_by_username.return_value = existing

    dto = UserRegistrationDTO("existente", "passwordSeguro1", "Juan Perez")
    with pytest.raises(UserAlreadyExistsError, match="ya está registrado"):
        core_service.register_user(dto)


def test_authenticate_user_success_admin(app_context, core_service, mock_user_dao):
    hashed = hash_password("admin123")
    user = UserEntity(1, "admin", hashed, "Admin Principal", is_admin=True)
    mock_user_dao.get_by_username.return_value = user

    authenticated = core_service.authenticate_user(LoginDTO("admin", "admin123"))

    assert authenticated.username == "admin"
    assert session.get("user_id") == 1
    assert session.get("role") == "ADMIN"


def test_authenticate_user_success_regular(app_context, core_service, mock_user_dao):
    hashed = hash_password("clave12345")
    user = UserEntity(2, "lector", hashed, "Lector Regular", is_admin=False)
    mock_user_dao.get_by_username.return_value = user

    core_service.authenticate_user(LoginDTO("lector", "clave12345"))
    assert session.get("role") == "USER"


def test_authenticate_user_invalid_username(app_context, core_service, mock_user_dao):
    mock_user_dao.get_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError):
        core_service.authenticate_user(LoginDTO("inexistente", "clave"))


def test_authenticate_user_wrong_password(app_context, core_service, mock_user_dao):
    hashed = hash_password("clave_correcta")
    user = UserEntity(1, "lector", hashed, "Lector")
    mock_user_dao.get_by_username.return_value = user

    with pytest.raises(InvalidCredentialsError):
        core_service.authenticate_user(LoginDTO("lector", "clave_erronea"))


def test_logout_user(app_context, core_service):
    session["user_id"] = 1
    session["role"] = "ADMIN"

    core_service.logout_user()

    assert "user_id" not in session
    assert "role" not in session


def test_log_visitor_success(core_service, mock_visitor_log_dao):
    def fake_save(log):
        log.id = 55
        return log

    mock_visitor_log_dao.save.side_effect = fake_save

    dto = VisitorLogDTO("V-12345", "Carlos", "0414")
    saved = core_service.log_visitor(dto)

    assert saved.id == 55
    assert saved.visitor_name == "Carlos"


def test_log_visitor_failure(core_service, mock_visitor_log_dao):
    def fake_save(log):
        log.id = None
        return log

    mock_visitor_log_dao.save.side_effect = fake_save

    dto = VisitorLogDTO("V-12345", "Carlos", "0414")
    with pytest.raises(VisitorLogCreationError):
        core_service.log_visitor(dto)


def test_get_visitor_logs_pagination(core_service, mock_visitor_log_dao):
    logs = [
        VisitorLogEntity(1, "V-1", "A", None),
        VisitorLogEntity(2, "V-2", "B", None),
    ]
    mock_visitor_log_dao.get_paginated.return_value = (logs, 15)

    result = core_service.get_visitor_logs(page=2, per_page=5)

    assert result["total_count"] == 15
    assert result["current_page"] == 2
    assert result["total_pages"] == 3
    assert len(result["logs"]) == 2


def test_get_visitor_analytics_growth_positive(core_service, mock_visitor_log_dao):
    d1 = datetime(2026, 4, 1)
    d2 = datetime(2026, 4, 2)
    mock_visitor_log_dao.get_aggregated_stats.return_value = [
        {"period": d1, "count": 10},
        {"period": d2, "count": 15},
    ]

    analytics = core_service.get_visitor_analytics(
        start_str="2026-04-01", end_str="2026-04-02"
    )

    assert analytics["total_visits"] == 25
    assert analytics["growth_pct"] == 50.0
    assert analytics["labels"] == ["2026-04-01", "2026-04-02"]
    assert analytics["values"] == [10, 15]


def test_get_visitor_analytics_growth_zero_previous(core_service, mock_visitor_log_dao):
    d1 = datetime(2026, 4, 1)
    d2 = datetime(2026, 4, 2)
    mock_visitor_log_dao.get_aggregated_stats.return_value = [
        {"period": d1, "count": 0},
        {"period": d2, "count": 20},
    ]

    analytics = core_service.get_visitor_analytics(
        start_str="2026-04-01", end_str="2026-04-02"
    )
    assert analytics["growth_pct"] == 0


def test_get_visitor_analytics_insufficient_data(core_service, mock_visitor_log_dao):
    d1 = datetime(2026, 4, 1)
    mock_visitor_log_dao.get_aggregated_stats.return_value = [
        {"period": d1, "count": 8}
    ]

    analytics = core_service.get_visitor_analytics()
    assert analytics["total_visits"] == 8
    assert analytics["growth_pct"] == 0
