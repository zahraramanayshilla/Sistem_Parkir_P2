# app/models/parkir_model.py

from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from app.models.db_models import User, ParkirLog
from bson import ObjectId


class ParkirModel:

    TOTAL_SLOT = 250
    SCAN_COOLDOWN = 5  # detik

    # ============================
    # LOGIN
    # ============================
    @staticmethod
    def validate_login(username: str, password: str):
        """
        Cari user berdasarkan username, lalu cek password hash.
        Return:
          - user (objek User MongoEngine) kalau berhasil,
          - None kalau gagal.
        """
        if not username or not password:
            return None

        user = User.objects(username=username).first()
        if not user:
            return None

        # password tersimpan sebagai hash
        if check_password_hash(user.password, password):
            return user

        return None

    # ============================
    # USER HELPERS
    # ============================
    @staticmethod
    def get_user_by_id(user_id: str):
        if not user_id:
            return None
        try:
            return User.objects(id=ObjectId(user_id)).first()
        except Exception:
            return None

    @staticmethod
    def get_all_users():
        """
        Ambil semua user (admin + petugas)
        """
        return User.objects().order_by("username")

    @staticmethod
    def get_petugas():
        """
        Ambil semua user dengan role 'petugas'
        """
        return User.objects(role="petugas").order_by("username")

    # ==================================================
    # LOGIKA SCAN QR DARI ESP32
    # ==================================================
    @staticmethod
    def process_scan(nomor: str, npm: str, nama: str):
        """
        Logika FINAL scan parkir:
        - Scan pertama  -> MASUK
        - Scan kedua    -> KELUAR + hitung durasi
        - Anti double scan aktif
        """

        npm = (npm or "").strip()
        nama = (nama or "-").strip()

        if not npm:
            return False, "NPM kosong", None

        now = datetime.utcnow()

        # ==========================
        # LOG TERAKHIR BERDASARKAN NPM
        # ==========================
        last_log = ParkirLog.objects(npm=npm).order_by("-waktu_masuk").first()

        # ==========================
        # ANTI DOUBLE SCAN
        # ==========================
        if last_log:
            last_time = last_log.waktu_keluar or last_log.waktu_masuk
            if last_time:
                delta = (now - last_time).total_seconds()
                if delta < ParkirModel.SCAN_COOLDOWN:
                    return (
                        False,
                        "SCAN_TOO_FAST",
                        ParkirModel.get_dashboard_stats(),
                    )

        # ==========================
        # SCAN PERTAMA → MASUK
        # ==========================
        if not last_log or last_log.status == "keluar":
            ParkirLog(
                nomor=nomor,
                npm=npm,
                nama=nama,
                waktu_masuk=now,
                status="masuk",
            ).save()

            stats = ParkirModel.get_dashboard_stats()
            return (
                True,
                "MASUK",
                {
                    **stats,
                    "durasi": "—",
                },
            )

        # ==========================
        # SCAN KEDUA → KELUAR
        # ==========================
        last_log.waktu_keluar = now
        last_log.status = "keluar"
        last_log.save()

        # Hitung durasi
        durasi_detik = int((now - last_log.waktu_masuk).total_seconds())
        jam = durasi_detik // 3600
        menit = (durasi_detik % 3600) // 60
        durasi_str = f"{jam}j {menit}m" if jam else f"{menit}m"

        stats = ParkirModel.get_dashboard_stats()

        return (
            True,
            "KELUAR",
            {
                **stats,
                "durasi": durasi_str,
                "durasi_detik": durasi_detik,
            },
        )

    # ==================================================
    # STATISTIK DASHBOARD (TANPA SLOT)
    # ==================================================
    @staticmethod
    def get_dashboard_stats():
        now = datetime.utcnow()
        start_today = datetime(now.year, now.month, now.day)
        end_today = start_today + timedelta(days=1)

        # Kendaraan yang sedang parkir
        sedang_di_dalam = ParkirLog.objects(
            status="masuk", waktu_keluar__exists=False
        ).count()

        # Total scan hari ini
        total_scan_hari_ini = ParkirLog.objects(
            waktu_masuk__gte=start_today, waktu_masuk__lt=end_today
        ).count()

        # Rata-rata durasi parkir hari ini (yang sudah keluar)
        logs_today = ParkirLog.objects(
            waktu_keluar__gte=start_today, waktu_keluar__lt=end_today
        )

        total_detik = 0
        n = 0
        for log in logs_today:
            if log.waktu_masuk and log.waktu_keluar:
                delta = log.waktu_keluar - log.waktu_masuk
                total_detik += int(delta.total_seconds())
                n += 1

        avg_detik = total_detik // n if n else 0
        jam = avg_detik // 3600
        menit = (avg_detik % 3600) // 60
        rata_rata_str = f"{jam}j {menit}m" if n else "—"

        return {
            "sedang_di_dalam": sedang_di_dalam,
            "total_scan_hari_ini": total_scan_hari_ini,
            "rata_rata_str": rata_rata_str,
            "avg_detik": avg_detik,
        }

    # ============================
    # VALIDASI QR (UNTUK MQTT)
    # ============================
    @staticmethod
    def validate_user(npm: str, nama: str) -> bool:
        if not npm:
            return False
        if not npm.isdigit():   # NPM harus angka
            return False
        return True


# ==================================================
# OPSIONAL: SIMPAN RAW DATA QR (AUDIT / DEBUG)
# ==================================================
class ParkirQR:
    def __init__(self, db):
        self.collection = db.parkir_qr

    def simpan(self, data: dict):
        data["waktu"] = datetime.now()
        self.collection.insert_one(data)
