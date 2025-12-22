from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash
from app.models.db_models import User
from app.models.parkir_model import ParkirModel

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu", "warning")
            return redirect(url_for("dashboard.login"))
        return f(*args, **kwargs)
    return decorated_function


# ============================
# ROLE REQUIRED
# ============================
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Silakan login terlebih dahulu", "warning")
                return redirect(url_for("dashboard.login"))

            if session.get("role") not in roles:
                flash("Anda tidak memiliki hak akses.", "error")
                return redirect(url_for("dashboard.index"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================
# LOGIN
# ============================
@dashboard_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = ParkirModel.validate_login(username, password)

        if user:
            session["user_id"] = str(user.id)
            session["username"] = user.username
            session["role"] = user.role

            flash(f"Selamat datang, {user.username}!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Username atau password salah", "error")

    return render_template("login.html", mode="login")


# ============================
# REGISTER
# ============================
@dashboard_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # Validasi basic
        if not all([email, username, password, confirm]):
            flash("Semua field harus diisi.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Password dan konfirmasi password tidak cocok.", "error")
            return render_template("register.html")

        # Cek duplikasi
        if User.objects(username=username).first():
            flash("Username sudah digunakan.", "error")
            return render_template("register.html")

        if User.objects(email=email).first():
            flash("Email sudah terdaftar.", "error")
            return render_template("register.html")

        # Semua yang daftar = PETUGAS
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role="petugas"
        )
        user.save()

        flash("Registrasi berhasil! Silakan login.", "success")
        return redirect(url_for("dashboard.login"))

    # GET
    return render_template("register.html")


# ============================
# LOGOUT
# ============================
@dashboard_bp.route("/logout")
def logout():
    session.clear()
    flash("Anda telah logout", "info")
    return redirect(url_for("dashboard.login"))


# ============================
# DASHBOARD UTAMA
# ============================
@dashboard_bp.route("/")
@login_required
def index():
    # data awal (sekali saja, pakai Jinja)
    from app.models.db_models import ParkirLog

    logs = ParkirLog.objects.order_by("-waktu_masuk")[:20]
    return render_template("index.html", logs=logs)


# ============================
# RIWAYAT (ADMIN SAJA)
# ============================
@dashboard_bp.route("/riwayat")
@login_required
@role_required("petugas","admin")
def riwayat():
    return render_template("riwayat.html")


# ============================
# MONITORING (PETUGAS + ADMIN)
# ============================
@dashboard_bp.route("/monitoring")
@login_required
@role_required("petugas", "admin")
def monitoring():
    return render_template("monitoring.html")


# ============================
# PENGATURAN (ADMIN SAJA)
# ============================
@dashboard_bp.route("/pengaturan")
@login_required
@role_required("admin")
def pengaturan():
    petugas = ParkirModel.get_petugas()
    semua = ParkirModel.get_all_users()
    return render_template("pengaturan.html", petugas=petugas, semua=semua)


# ============================================================
# PROFILE PAGE — ADMIN & PETUGAS
# ============================================================
@dashboard_bp.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    current_user = ParkirModel.get_user_by_id(user_id)

    # kalau user nggak ketemu di Mongo
    if not current_user:
        flash("User tidak ditemukan. Silakan login ulang.", "error")
        # bersihkan session & paksa login ulang
        session.clear()
        return redirect(url_for("dashboard.login"))

    role = current_user.role

    is_admin = (role == "admin")
    is_petugas = (role == "petugas")

    # daftar user untuk tabel
    if is_admin:
        users = ParkirModel.get_all_users()
    else:
        users = ParkirModel.get_petugas()

    return render_template(
        "profile.html",
        current_user=current_user,
        users=users,
        is_admin=is_admin,
        is_petugas=is_petugas,
    )


# ============================================================
# UPDATE PROFIL SENDIRI
# ============================================================
@dashboard_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    user = ParkirModel.get_user_by_id(session["user_id"])

    username = request.form["username"].strip()
    email = request.form["email"].strip()
    password = request.form.get("password", "")

    # validasi duplikat
    if User.objects(username=username, id__ne=user.id).first():
        flash("Username sudah terpakai!", "error")
        return redirect(url_for("dashboard.profile"))

    if User.objects(email=email, id__ne=user.id).first():
        flash("Email sudah digunakan!", "error")
        return redirect(url_for("dashboard.profile"))

    user.username = username
    user.email = email

    if password:
        user.password = generate_password_hash(password)

    user.save()
    flash("Profil berhasil diperbarui!", "success")
    return redirect(url_for("dashboard.profile"))


# ============================================================
# UPDATE USER LAIN (ADMIN SAJA)
# ============================================================
@dashboard_bp.route("/users/<user_id>/update", methods=["POST"])
@login_required
@role_required("admin")
def update_user(user_id):
    user = User.objects(id=user_id).first()

    if not user:
        flash("User tidak ditemukan", "error")
        return redirect(url_for("dashboard.profile"))

    username = request.form["username"].strip()
    email = request.form["email"].strip()
    role = request.form.get("role", "petugas")
    password = request.form.get("password", "")

    # Validasi username
    if User.objects(username=username, id__ne=user.id).first():
        flash("Username sudah digunakan!", "error")
        return redirect(url_for("dashboard.profile"))

    # Validasi email
    if User.objects(email=email, id__ne=user.id).first():
        flash("Email sudah digunakan!", "error")
        return redirect(url_for("dashboard.profile"))

    user.username = username
    user.email = email

    if role in ("admin", "petugas"):
        user.role = role

    if password:
        user.password = generate_password_hash(password)

    user.save()
    flash("Data user berhasil diperbarui!", "success")
    return redirect(url_for("dashboard.profile"))


# ============================================================
# DELETE USER (ADMIN)
# ============================================================
@dashboard_bp.route("/delete_user/<user_id>")
@login_required
@role_required("admin")
def delete_user(user_id):
    user = User.objects(id=user_id).first()

    if not user:
        flash("User tidak ditemukan!", "error")
        return redirect(url_for("dashboard.profile"))

    if str(user.id) == session["user_id"]:
        flash("Tidak dapat menghapus akun sendiri!", "error")
        return redirect(url_for("dashboard.profile"))

    user.delete()
    flash("User berhasil dihapus!", "success")
    return redirect(url_for("dashboard.profile"))
