# app/models/db_models.py
from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    ReferenceField,
)
from datetime import datetime


class User(Document):
    meta = {
        "collection": "users",  # nama collection di MongoDB
    }

    username = StringField(required=True, unique=True, max_length=100)
    email = EmailField(required=True, unique=True, max_length=120)
    password = StringField(required=True, max_length=200)
    role = StringField(default="mahasiswa", max_length=20)
    created_at = DateTimeField(default=datetime.utcnow)


class ParkirLog(Document):
    meta = {
        "collection": "parkir_logs",
    }

    # relasi ke User (ganti user_id integer → ReferenceField)
    user = ReferenceField(User, required=True)

    waktu_masuk = DateTimeField(default=datetime.utcnow)
    waktu_keluar = DateTimeField(null=True)
    status = StringField(default="masuk", max_length=20)
