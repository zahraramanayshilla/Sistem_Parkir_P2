# app/models/parkir_model.py
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from app.models.db_models import User, ParkirLog


class ParkirModel:

    # ==================== LOGIN ====================
    @staticmethod
    def validate_login(username, password):
        # Cari user berdasarkan username
        user = User.objects(username=username).first()

        # Password sudah di-hash, jadi pakai check_password_hash
        if user and check_password_hash(user.password, password):
            return user  # return object User (Document)
        return None

    # ==================== REGISTER ====================
    @staticmethod
    def register_user(username, email, password):

        # cek username dipakai?
        if User.objects(username=username).first():
            return False, "Username sudah digunakan."

        # cek email dipakai?
        if User.objects(email=email).first():
            return False, "Email sudah terdaftar."

        hashed = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed,
            role="mahasiswa",
        )
        user.save()
        return True, "User berhasil didaftarkan."

    # ==================== LOG PARKIR ====================
    @staticmethod
    def create_parkir_log(user_id):
        user = User.objects(id=user_id).first()
        if not user:
            return None

        log = ParkirLog(user=user)
        log.save()
        return log

    @staticmethod
    def update_keluar(log_id):
        log = ParkirLog.objects(id=log_id).first()
        if log:
            log.waktu_keluar = datetime.utcnow()
            log.status = "keluar"
            log.save()
            return True
        return False

    # ==================== GET DATA ====================
    @staticmethod
    def get_all_logs():
        # log terbaru dulu
        return ParkirLog.objects.order_by("-waktu_masuk")

    @staticmethod
    def get_user_by_id(user_id):
        return User.objects(id=user_id).first()

    @staticmethod
    def get_all_users():
        return User.objects.order_by("created_at")
