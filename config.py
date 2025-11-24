import os


class Config:
    # URL database PostgreSQL
    # Format: postgresql://username:password@host:port/nama_database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:Zahra123.@localhost:5432/sistem_parkir"
    )

    # Mematikan track modifications agar tidak ada warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key untuk session atau csrf (opsional tapi disarankan)
    SECRET_KEY = os.getenv("SECRET_KEY", "ini_secret_key_default")
