from flask import Flask


def create_app():
    app = Flask(__name__)

    # Import blueprint dari controller
    from app.controllers.dashboard_controller import dashboard_bp

    app.register_blueprint(dashboard_bp)

    return app
