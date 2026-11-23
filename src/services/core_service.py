from datetime import datetime, timedelta

from flask import session

from src.contracts.core_contracts import IUserDAO, IVisitorLogDAO
from src.dtos.core_dtos import LoginDTO, UserRegistrationDTO, VisitorLogDTO
from src.entities.core_entities import UserEntity, VisitorLogEntity
from src.exceptions.core_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    VisitorLogCreationError,
)
from src.utils.security import hash_password, verify_password


class CoreService:
    def __init__(self, user_dao: IUserDAO, visitor_log_dao: IVisitorLogDAO):
        self.user_dao = user_dao
        self.visitor_log_dao = visitor_log_dao

    def register_user(self, dto: UserRegistrationDTO) -> UserEntity:
        existing_user = self.user_dao.get_by_username(dto.username)
        if existing_user is not None:
            raise UserAlreadyExistsError(
                f"El nombre de usuario '{dto.username}' ya está registrado."
            )

        hashed_password = hash_password(dto.password)
        new_user = UserEntity(
            id=None,
            username=dto.username,
            password_hash=hashed_password,
            full_name=dto.full_name,
            is_admin=False,
            is_active=True,
        )

        saved_user = self.user_dao.save(new_user)

        session["user_id"] = saved_user.id
        session["role"] = "USER"

        return saved_user

    def authenticate_user(self, dto: LoginDTO) -> UserEntity:
        user = self.user_dao.get_by_username(dto.username)
        if user is None:
            raise InvalidCredentialsError("Credenciales inválidas.")

        if not verify_password(dto.password, user.password_hash):
            raise InvalidCredentialsError("Credenciales inválidas.")

        session["user_id"] = user.id
        session["role"] = "ADMIN" if user.is_admin else "USER"

        return user

    def logout_user(self) -> None:
        session.clear()

    def log_visitor(self, dto: VisitorLogDTO) -> VisitorLogEntity:
        new_log = VisitorLogEntity(
            id=None,
            visitor_id=dto.visitor_id,
            visitor_name=dto.visitor_name,
            contact_info=dto.contact_info,
        )
        saved_log = self.visitor_log_dao.save(new_log)
        if not saved_log.id:
            raise VisitorLogCreationError("No se pudo registrar la visita.")
        return saved_log

    def get_visitor_logs(
        self, search_name: str = "", page: int = 1, per_page: int = 10
    ) -> dict:
        logs, total_count = self.visitor_log_dao.get_paginated(
            search_name=search_name, page=page, per_page=per_page
        )
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

        return {
            "logs": logs,
            "total_count": total_count,
            "current_page": page,
            "total_pages": total_pages,
            "search_name": search_name,
        }

    def get_visitor_analytics(
        self,
        start_str: str | None = None,
        end_str: str | None = None,
        interval: str = "day",
    ):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        if start_str:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
        if end_str:
            end_date = datetime.strptime(end_str, "%Y-%m-%d")

        stats = self.visitor_log_dao.get_aggregated_stats(
            start_date, end_date, interval
        )

        total_visits = sum(s["count"] for s in stats)
        growth_pct = 0
        if len(stats) >= 2:
            current = stats[-1]["count"]
            previous = stats[-2]["count"]
            if previous > 0:
                growth_pct = ((current - previous) / previous) * 100

        return {
            "labels": [s["period"].strftime("%Y-%m-%d") for s in stats],
            "values": [s["count"] for s in stats],
            "total_visits": total_visits,
            "growth_pct": round(growth_pct, 2),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "interval": interval,
        }
