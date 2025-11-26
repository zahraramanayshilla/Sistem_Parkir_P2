# app/controllers/dashboard_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.parkir_model import ParkirModel
from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "error")
            return redirect(url_for("dashboard.login"))
        return f(*args, **kwargs)

    return decorated_function


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="")


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu", "warning")
            return redirect(url_for("dashboard.login"))
        return f(*args, **kwargs)

    return decorated_function


@dashboard_bp.route("/")
@login_required
def index():
    return render_template("index.html")


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
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user.get("role", "user")
            flash(f'Selamat datang, {user["username"]}!', "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Username atau password salah", "error")
            return render_template("login.html")

    return render_template("login.html")


@dashboard_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        email = request.form.get("email", "").strip()

        # cek semua field wajib diisi
        if not all([username, password, confirm_password, email]):
            flash("Semua field harus diisi", "error")
            return render_template("register.html")

        # cek password cocok
        if password != confirm_password:
            flash("Password dan konfirmasi password tidak cocok", "error")
            return render_template("register.html")

        # cek username sudah ada
        from app.models.db_models import User
        from app import db

        if User.query.filter_by(username=username).first():
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
            db.session.rollback()
            flash(f"Registrasi gagal: {e}", "error")
            return render_template("register.html")

    return render_template("register.html")


@dashboard_bp.route("/logout")
def logout():
    session.clear()
    flash("Anda telah logout", "info")
    return redirect(url_for("dashboard.login"))
