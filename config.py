import os
from datetime import timedelta
from flask import Flask


class Config:
    """
    Base configuration class.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(os.getcwd(), "flask_session")
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_KEY_PREFIX = "shophive:"
    SESSION_FILE_THRESHOLD = 500
    SESSION_FILE_MODE = 0o600
    SESSION_COOKIE_NAME = "shophive_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_REFRESH_EACH_REQUEST = True

    @staticmethod
    def init_app(app: 'Flask') -> None:
        os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)


class DevelopmentConfig(Config):
    """
    Development configuration class.
    """
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASS = os.getenv('DB_PASS', 'postgres')
    DB_NAME = os.getenv('DB_NAME', 'shophive')
    DB_HOST = os.getenv('DB_HOST', 'localhost')

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASS}"
        f"@{DB_HOST}/{DB_NAME}"
    )


class TestingConfig(Config):
    """
    Testing configuration class.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
