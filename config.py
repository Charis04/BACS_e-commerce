import os
from datetime import timedelta


class Config:
    """
    Base configuration class.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_jwt_secret_key")
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_TYPE = "filesystem"


class DevelopmentConfig(Config):
    """
    Development configuration class.
    """

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL",
                                        "sqlite:///shophive.db")


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
