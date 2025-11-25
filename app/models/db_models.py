from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="mahasiswa")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ParkirLog(db.Model):
    __tablename__ = "parkir_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    waktu_masuk = db.Column(db.DateTime, default=datetime.utcnow)
    waktu_keluar = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="masuk")
