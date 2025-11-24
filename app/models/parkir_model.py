from app import db
from sqlalchemy import text


class ParkirModel:
    @staticmethod
    def check_username_exists(username):
        """Cek apakah username sudah terdaftar"""
        result = db.session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username},
        ).fetchone()
        return result is not None

    @staticmethod
    def register_user(username, password, email, full_name):
        """Tambah user baru ke database"""
        try:
            db.session.execute(
                text(
                    "INSERT INTO users (username, password, email, full_name) "
                    "VALUES (:username, :password, :email, :full_name)"
                ),
                {
                    "username": username,
                    "password": password,
                    "email": email,
                    "full_name": full_name,
                },
            )
            db.session.commit()
            return True
        except Exception as e:
            print("Error register_user:", e)
            db.session.rollback()
            return False

    @staticmethod
    def validate_login(username, password):
        """Validasi login"""
        user = db.session.execute(
            text(
                "SELECT * FROM users WHERE username = :username AND password = :password"
            ),
            {"username": username, "password": password},
        ).fetchone()
        if user:
            return dict(user)
        return None
