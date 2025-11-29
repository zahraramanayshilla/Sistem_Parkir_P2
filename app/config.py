# app/config.py
import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ini_secret_key_default_please_change")

    # Konfigurasi MongoDB
    MONGODB_SETTINGS = {
        "db": os.getenv("MONGO_DB_NAME", "sistem_parkir"),
        "host": os.getenv("MONGO_URI", "mongodb://localhost:27017/sistem_parkir"),
        # Kalau pakai username/password:
        # "username": os.getenv("MONGO_USER"),
        # "password": os.getenv("MONGO_PASS"),
    }

    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
