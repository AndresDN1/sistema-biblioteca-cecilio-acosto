import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UserRegistrationDTO:
    username: str
    password: str
    full_name: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "UserRegistrationDTO":
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", ""))
        full_name = str(data.get("full_name", "")).strip()

        if not username:
            raise ValueError("Nombre de usuario requerido.")

        if len(username) < 3 or len(username) > 20:
            raise ValueError("El nombre de usuario debe tener entre 3 y 20 caracteres.")

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValueError(
                "El nombre de usuario solo puede contener letras, números y guiones bajos."
            )

        if not password:
            raise ValueError("Contraseña requerida.")

        if len(password) < 8 or len(password) > 128:
            raise ValueError("La contraseña debe tener entre 8 y 128 caracteres.")

        if not full_name:
            raise ValueError("El nombre completo es requerido.")

        return cls(
            username=username,
            password=password,
            full_name=full_name,
        )


@dataclass(frozen=True)
class LoginDTO:
    username: str
    password: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LoginDTO":
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", ""))

        if not username:
            raise ValueError("Nombre de usuario requerido.")

        if not password:
            raise ValueError("Contraseña requerida.")

        return cls(username=username, password=password)


@dataclass(frozen=True)
class VisitorLogDTO:
    visitor_id: str
    visitor_name: str
    contact_info: str | None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "VisitorLogDTO":
        visitor_id = str(data.get("visitor_id", "")).strip()
        visitor_name = str(data.get("visitor_name", "")).strip()
        contact_info = data.get("contact_info")

        if contact_info is not None:
            contact_info = str(contact_info).strip() or None

        if not visitor_id:
            raise ValueError("Identificación del visitante requerida.")

        if not visitor_name:
            raise ValueError("Nombre del visitante requerido.")

        return cls(
            visitor_id=visitor_id,
            visitor_name=visitor_name,
            contact_info=contact_info,
        )
