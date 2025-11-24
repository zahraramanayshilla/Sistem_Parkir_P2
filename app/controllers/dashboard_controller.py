# app/controllers/dashboard_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.parkir_model import ParkirModel

dashboard_bp = Blueprint("dashboard", __name__)


# ==================== DECORATOR LOGIN ====================
def login_required(f):
    """Decorator untuk memastikan user sudah login"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu", "warning")
            return redirect(url_for("dashboard.login"))
        return f(*args, **kwargs)

    return decorated_function


# ==================== INDEX DASHBOARD ====================
@dashboard_bp.route("/")
@login_required
def index():
    """Halaman utama dashboard"""
    return render_template("index.html")


# ==================== LOGIN ====================
@dashboard_bp.route("/login", methods=["GET", "POST"])
def login():
    """Halaman dan proses login"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

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


# ==================== REGISTER ====================
@dashboard_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if ParkirModel.check_username_exists(username):
            flash("Username sudah digunakan", "error")
            return render_template("register.html")

        success = ParkirModel.register_user(username, password, email)
        if success:
            flash("Registrasi berhasil! Silakan login", "success")
            return redirect(url_for("dashboard.login"))
        else:
            flash("Registrasi gagal", "error")
            return render_template("register.html")

    return render_template("register.html")


# ==================== LOGOUT ====================
@dashboard_bp.route("/logout")
def logout():
    """Logout user dan hapus session"""
    session.clear()
    flash("Anda telah logout", "info")
    return redirect(url_for("dashboard.login"))
