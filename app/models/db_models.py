from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    ReferenceField,
)


class User(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(default="petugas")  # atau "admin"


class ParkirLog(Document):
    npm = StringField(required=True)  # dari QR
    nama = StringField()  # dari QR
    waktu_masuk = DateTimeField()
    waktu_keluar = DateTimeField()
    status = StringField(choices=("masuk", "keluar"), required=True)
