from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserEntity:
    id: int | None
    username: str
    password_hash: str
    full_name: str
    is_admin: bool = False
    is_active: bool = True


@dataclass
class VisitorLogEntity:
    id: int | None
    visitor_id: str
    visitor_name: str
    contact_info: str | None
    check_in: datetime | None = None
