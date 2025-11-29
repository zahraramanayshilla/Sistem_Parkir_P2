# app/models/__init__.py

from app.models.db_models import User, ParkirLog
from app.models.parkir_model import ParkirModel

__all__ = ["User", "ParkirLog", "ParkirModel"]
