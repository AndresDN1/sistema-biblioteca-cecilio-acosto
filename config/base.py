import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    APP_NAME = "Librería Cecilio Acosto"
    ITEMS_PER_PAGE = 10
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "c0a592e38480d36f62cef3cf118b0925f26ba30b905bc1369e5c8481bcc6ef80"
    )
