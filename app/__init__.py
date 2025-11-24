from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# ================== INIT ==================
db = SQLAlchemy()  # instance SQLAlchemy


def create_app():
    app = Flask(__name__, template_folder="app/views/templates")
    app.config["SECRET_KEY"] = "your-secret-key-here"
    # ganti dengan URL database PostgreSQL kamu
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:pasZahra123.sword@localhost:5432/sistem_parkir"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)  # hubungkan db ke app

    # Import blueprint
    from app.controllers.dashboard_controller import dashboard_bp

    app.register_blueprint(dashboard_bp)

    return app
