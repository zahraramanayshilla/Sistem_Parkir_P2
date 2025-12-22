# app/__init__.py

from flask import Flask
import mongoengine
from app.controllers.socket_controller import socketio


def create_app(config_object=None):
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )

    # =========================
    # LOAD CONFIG
    # =========================
    if config_object is None:
        from app.config import Config

        app.config.from_object(Config)
    else:
        app.config.from_object(config_object)

    # =========================
    # MONGODB (MongoEngine)
    # =========================
    mongo_cfg = app.config.get("MONGODB_SETTINGS", {})
    mongoengine.connect(
        db=mongo_cfg.get("db", "sistem_parkir"),
        host=mongo_cfg.get("host", "mongodb://localhost:27017/sistem_parkir"),
        username=mongo_cfg.get("username"),
        password=mongo_cfg.get("password"),
    )

    # =========================
    # SOCKET.IO
    # =========================
    socketio.init_app(app)

    # =========================
    # REGISTER BLUEPRINT
    # =========================
    from app.controllers.dashboard_controller import dashboard_bp

    app.register_blueprint(dashboard_bp)

    return app
