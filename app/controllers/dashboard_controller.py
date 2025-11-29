from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps

from werkzeug.security import generate_password_hash
from app.models.parkir_model import ParkirModel
from app.models.db_models import User

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="")



# ============================
# LOGIN REQUIRED DECORATOR
# ============================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu", "warning")
            return redirect(url_for("dashboard.login"))
        return f(*args, **kwargs)

    return decorated_function


# ============================
# HALAMAN LOGIN
# ============================
@dashboard_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username dan password harus diisi", "error")
            return render_template("login.html")

        user = ParkirModel.validate_login(username, password)

        if user:
            # user adalah object Document (MongoEngine)
            session["user_id"] = str(user.id)  # ObjectId -> string
            session["username"] = user.username
            session["role"] = getattr(user, "role", "user")

            flash(f"Selamat datang, {user.username}!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Username atau password salah", "error")
            return render_template("login.html")

    return render_template("login.html")


# ============================
# HALAMAN REGISTER
# ============================
@dashboard_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        email = request.form.get("email", "").strip()

        if not all([username, password, confirm_password, email]):
            flash("Semua field harus diisi", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Password dan konfirmasi password tidak cocok", "error")
            return render_template("register.html")

        if User.objects(username=username).first():
            flash("Username sudah digunakan", "error")
            return render_template("register.html")

        # buat user baru
        new_user = User(
            username=username, email=email, password=password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registrasi berhasil! Silakan login", "success")
            return redirect(url_for("dashboard.login"))
        except Exception as e:
            flash(f"Registrasi gagal: {e}", "error")
            return render_template("register.html")

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
# HALAMAN DASHBOARD
# ============================
@dashboard_bp.route("/")
@login_required
def index():
    return render_template("index.html")


# ============================
# HALAMAN RIWAYAT
# ============================
@dashboard_bp.route("/riwayat")
@login_required
def riwayat():
    return render_template("riwayat.html")


# ============================
# HALAMAN MONITORING
# ============================
@dashboard_bp.route("/monitoring")
@login_required
def monitoring():
    return render_template("monitoring.html")


# ============================
# HALAMAN PENGATURAN
# ============================
@dashboard_bp.route("/pengaturan")
@login_required
def pengaturan():
    return render_template("pengaturan.html")


# ============================
# HALAMAN PROFILE
# ============================
@dashboard_bp.route("/profile")
@login_required
def profile():
    users = ParkirModel.get_all_users()  # jika ingin menampilkan data pengguna
    return render_template("profile.html", users=users)
