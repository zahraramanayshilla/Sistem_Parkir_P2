from app import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.db_models import User, ParkirLog
from sqlalchemy import text

class ParkirModel:

    # ==================== LOGIN ====================
    @staticmethod
    def validate_login(username, password):
        row = db.session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if row:
            # Konversi Row menjadi dict
            user = dict(row._mapping)  # <-- gunakan _mapping
            if user["password"] == password:
                return user

        return None


    # ==================== REGISTER ====================
    @staticmethod
    def register_user(full_name, username, email, password):

        # cek username dipakai?
        if User.query.filter_by(username=username).first():
            return False, "Username sudah digunakan."

        # cek email dipakai?
        if User.query.filter_by(email=email).first():
            return False, "Email sudah terdaftar."

        hashed = generate_password_hash(password)

        user = User(
            full_name=full_name, username=username, email=email, password=hashed
        )

        db.session.add(user)
        db.session.commit()
        return True, "User berhasil didaftarkan."

    # ==================== LOG PARKIR ====================
    @staticmethod
    def create_parkir_log(user_id):
        log = ParkirLog(user_id=user_id)
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def update_keluar(log_id):
        log = ParkirLog.query.get(log_id)
        if log:
            log.waktu_keluar = db.func.now()
            log.status = "keluar"
            db.session.commit()
            return True
        return False

    # ==================== GET DATA ====================
    @staticmethod
    def get_all_logs():
        return ParkirLog.query.order_by(ParkirLog.id.desc()).all()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
