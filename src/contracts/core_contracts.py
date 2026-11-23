from abc import ABC, abstractmethod
from datetime import datetime

from src.entities.core_entities import UserEntity, VisitorLogEntity


class IUserDAO(ABC):
    @abstractmethod
    def save(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> UserEntity | None:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> UserEntity | None:
        pass


class IVisitorLogDAO(ABC):
    @abstractmethod
    def save(self, log: VisitorLogEntity) -> VisitorLogEntity:
        pass

    @abstractmethod
    def get_paginated(
        self, search_name: str = "", page: int = 1, per_page: int = 10
    ) -> tuple[list[VisitorLogEntity], int]:
        pass

    @abstractmethod
    def get_aggregated_stats(
        self, start_date: datetime, end_date: datetime, interval: str = "day"
    ) -> list[dict]:
        pass
