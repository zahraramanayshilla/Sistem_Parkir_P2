from app import create_app
from app.controllers.socket_controller import socketio
from app.mqtt.mqtt_client import start_mqtt
import threading

app = create_app()


def run_mqtt(app):
    start_mqtt(app)


if __name__ == "__main__":
    # Jalankan MQTT di thread terpisah
    threading.Thread(target=run_mqtt, args=(app,), daemon=True).start()

    # Jalankan Flask + SocketIO
    socketio.run(app, debug=True, use_reloader=False)
