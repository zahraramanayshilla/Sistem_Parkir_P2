# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_object=None):
    app = Flask(
        __name__, template_folder="views/templates", static_folder="views/static"
    )

    # konfigurasi
    if config_object is None:
        from app.config import Config

        app.config.from_object(Config)
    else:
        app.config.from_object(config_object)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from app.controllers.dashboard_controller import dashboard_bp

    app.register_blueprint(dashboard_bp)

    return app
