# app/config.py
import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ini_secret_key_default_please_change")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:Zahra123.@localhost:5432/sistem_parkir"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optionally set debug via env
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
