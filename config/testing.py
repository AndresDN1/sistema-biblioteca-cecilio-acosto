from config.base import BaseConfig


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    ENV = "testing"
