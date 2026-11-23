from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from src.contracts.core_contracts import IUserDAO, IVisitorLogDAO
from src.entities.core_entities import UserEntity, VisitorLogEntity
from src.extensions import db
from src.models.core_models import UserModel, VisitorLogModel


class PostgresUserDAO(IUserDAO):
    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_admin=model.is_admin,
            is_active=model.is_active,
        )

    def save(self, user: UserEntity) -> UserEntity:
        try:
            if user.id is None:
                model = UserModel()
                model.username = user.username
                model.password_hash = user.password_hash
                model.full_name = user.full_name
                model.is_admin = user.is_admin
                model.is_active = user.is_active
                db.session.add(model)
            else:
                stmt = select(UserModel).where(UserModel.id == user.id)
                model = db.session.execute(stmt).scalars().first()
                if model is None:
                    raise KeyError(f"Usuario ID {user.id} no encontrado.")

                model.username = user.username
                model.password_hash = user.password_hash
                model.full_name = user.full_name
                model.is_admin = user.is_admin
                model.is_active = user.is_active

            db.session.commit()
            user.id = model.id
            return user
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def get_by_id(self, user_id: int) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        model = db.session.execute(stmt).scalars().first()
        return self._to_entity(model) if model else None

    def get_by_username(self, username: str) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.username == username)
        model = db.session.execute(stmt).scalars().first()
        return self._to_entity(model) if model else None


class PostgresVisitorLogDAO(IVisitorLogDAO):
    def _to_entity(self, model: VisitorLogModel) -> VisitorLogEntity:
        return VisitorLogEntity(
            id=model.id,
            visitor_id=model.visitor_id,
            visitor_name=model.visitor_name,
            contact_info=model.contact_info,
            check_in=model.check_in,
        )

    def save(self, log: VisitorLogEntity) -> VisitorLogEntity:
        try:
            model = VisitorLogModel()
            model.visitor_id = log.visitor_id
            model.visitor_name = log.visitor_name
            model.contact_info = log.contact_info

            db.session.add(model)
            db.session.commit()

            log.id = model.id
            log.check_in = model.check_in
            return log
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def get_paginated(
        self, search_name: str = "", page: int = 1, per_page: int = 10
    ) -> tuple[list[VisitorLogEntity], int]:
        stmt = select(VisitorLogModel)
        if search_name.strip():
            stmt = stmt.where(
                VisitorLogModel.visitor_name.ilike(f"%{search_name.strip()}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = db.session.execute(count_stmt).scalar() or 0

        stmt = (
            stmt
            .order_by(VisitorLogModel.check_in.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        models = db.session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in models], total_count

    def get_aggregated_stats(
        self, start_date: datetime, end_date: datetime, interval: str = "day"
    ) -> list[dict]:
        truncated_date = func.date_trunc(interval, VisitorLogModel.check_in)

        stmt = (
            select(
                truncated_date.label("period"),
                func.count(VisitorLogModel.id).label("count"),
            )
            .where(VisitorLogModel.check_in >= start_date)
            .where(VisitorLogModel.check_in <= end_date)
            .group_by("period")
            .order_by("period")
        )

        results = db.session.execute(stmt).all()
        return [{"period": r.period, "count": r.count} for r in results]
