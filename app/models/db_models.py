from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    ReferenceField,
)
from mongoengine import Document, StringField, EmailField, DateTimeField, ReferenceField
from datetime import datetime

from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime

class User(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(default="petugas")  # atau "admin"


class ParkirLog(Document):
    user = ReferenceField(User, required=True)
    waktu_masuk = DateTimeField(default=datetime.utcnow)
    waktu_keluar = DateTimeField()       # boleh kosong
    status = StringField(default="masuk")  # "masuk" / "keluar"
