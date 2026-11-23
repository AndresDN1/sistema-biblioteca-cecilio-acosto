import contextlib
import logging
import logging.handlers
import os

from flask import Flask

from src.extensions import db
from src.handlers.core_handlers import core_bp
from src.handlers.hooks import hooks_bp
from src.handlers.inventory_handlers import inventory_bp

from .utils import JsonFormatter


def initialize_app() -> Flask:
    src_path = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.abspath(os.path.join(src_path, "..", "instance"))
    app = Flask(__name__, root_path=src_path, instance_path=instance_path)
    settings_path = os.environ.get(
        "APP_SETTINGS", "config.development.DevelopmentConfig"
    )
    app.config.from_object(settings_path)

    with contextlib.suppress(OSError):
        os.makedirs(app.instance_path)

    configure_logging(app)
    db.init_app(app)
    app.register_blueprint(core_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(hooks_bp)
    app.logger.info("App setup successfully finished")
    return app


def configure_logging(app: Flask) -> None:
    log_path = os.path.join(app.instance_path, "logs.json")
    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=9 * 1024 * 1024, backupCount=9
    )
    file_handler.setFormatter(JsonFormatter())

    if app.config.get("DEBUG"):
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        app.logger.addHandler(console_handler)
    elif app.config.get("TESTING"):
        file_handler.setLevel(logging.WARNING)
    else:
        file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.propagate = False
