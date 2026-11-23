from .core_handlers import core_bp
from .hooks import hooks_bp
from .inventory_handlers import inventory_bp

__all__ = ["core_bp", "inventory_bp", "hooks_bp"]
