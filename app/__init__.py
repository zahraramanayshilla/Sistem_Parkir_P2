from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # hanya satu instance db


def create_app():
    app = Flask(__name__, template_folder="app/views/templates")
    app.config["SECRET_KEY"] = "your-secret-key-here"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:Zahra123.@localhost:5432/sistem_parkir"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # bind db ke app
    db.init_app(app)

    # register blueprint
    from app.controllers.dashboard_controller import dashboard_bp

    app.register_blueprint(dashboard_bp)

    return app
