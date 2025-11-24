from flask import Flask
from app.controllers.dashboard_controller import dashboard_bp


def create_app():
    app = Flask(__name__, template_folder="app/views/templates")
    app.config["SECRET_KEY"] = "your-secret-key-here"

    # Daftarkan blueprint
    app.register_blueprint(dashboard_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
