# app/models/parkir_model.py

from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from app.models.db_models import User, ParkirLog
from bson import ObjectId


class ParkirModel:
    """
    Semua operasi ke MongoDB yang berhubungan dengan user & log parkir.
    """

    TOTAL_SLOT = 250

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

    # ============================
    # LOGIKA SCAN QR
    # ============================
    @staticmethod
    def process_scan(kode: str):
        """
        Dipanggil saat QR KTM berhasil discan.
        Parameter 'kode' bisa kamu mapping ke field yang kamu pakai di User
        (misal username/NPM).

        Logika:
        - Cari user dari kode.
        - Kalau user punya log aktif (status='masuk' & belum ada waktu_keluar)
          -> anggap KELUAR.
        - Kalau tidak punya log aktif -> anggap MASUK.
        - Setelah itu hitung ulang statistik dashboard.
        Return:
          (ok: bool, aksi: 'masuk'/'keluar' atau pesan error, stats: dict | None)
        """
        kode = (kode or "").strip()
        if not kode:
            return False, "Kode QR kosong", None

        # Di sini aku anggap kode = username.
        # Kalau kamu pakai NPM, ganti jadi: User.objects(npm=kode).first()
        user = User.objects(username=kode).first()
        if not user:
            return False, "User tidak ditemukan", None

        # log aktif = sudah MASUK tapi belum ada waktu_keluar
        log_aktif = ParkirLog.objects(
            user=user,
            status="masuk",
            waktu_keluar__exists=False
        ).first()

        now = datetime.utcnow()

        if log_aktif:
            # QR discan lagi → KELUAR
            log_aktif.waktu_keluar = now
            log_aktif.status = "keluar"
            log_aktif.save()
            aksi = "keluar"
        else:
            # belum ada log aktif → ini MASUK
            ParkirLog(
                user=user,
                status="masuk",
                waktu_masuk=now
            ).save()
            aksi = "masuk"

        stats = ParkirModel.get_dashboard_stats()
        return True, aksi, stats

    # ============================
    # STATISTIK DASHBOARD
    # ============================
    @staticmethod
    def get_dashboard_stats():
        """
        Hitung data untuk card dashboard:
        - total_slot: kapasitas parkir
        - terpakai  : kendaraan yang sedang parkir (masuk & belum keluar)
        - tersedia  : total_slot - terpakai
        - rata_rata_str: rata-rata durasi parkir hari ini (yang sudah keluar) dalam format 'Xj Ym'
        """
        now = datetime.utcnow()
        start_today = datetime(now.year, now.month, now.day)
        end_today = start_today + timedelta(days=1)

        # TERPAKAI = log yang status 'masuk' dan belum ada waktu_keluar
        terpakai = ParkirLog.objects(
            status="masuk",
            waktu_keluar__exists=False
        ).count()

        tersedia = max(ParkirModel.TOTAL_SLOT - terpakai, 0)

        # RATA-RATA durasi parkir HARI INI (yang sudah keluar)
        logs_today = ParkirLog.objects(
            waktu_keluar__gte=start_today,
            waktu_keluar__lt=end_today
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
            "total_slot": ParkirModel.TOTAL_SLOT,
            "tersedia": tersedia,
            "terpakai": terpakai,
            "rata_rata_str": rata_rata_str,
            "avg_detik": avg_detik,
        }
