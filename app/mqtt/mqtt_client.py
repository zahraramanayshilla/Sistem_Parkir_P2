import paho.mqtt.client as mqtt
from datetime import datetime

from app.models.parkir_model import ParkirModel
from app.controllers.socket_controller import socketio

MQTT_TOPIC = "ulbiparkir/gate/qr"


def start_mqtt(app):
    client = mqtt.Client(client_id="flask-parkir-backend")

    # ================= CONNECT =================
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT CONNECTED")
            client.subscribe(MQTT_TOPIC)
        else:
            print("❌ MQTT FAILED, rc =", rc)

    # ================= MESSAGE =================
    def on_message(client, userdata, msg):
        with app.app_context():
            payload = msg.payload.decode().strip()
            print("📥 MQTT MASUK:", payload)

            # ESP baru nyala
            if payload == "READY":
                print("🟢 ESP ONLINE & READY")
                socketio.emit("esp_status", {"status": "READY"})
                return

            # Abaikan echo backend
            if payload in ("VALID", "INVALID"):
                return

            # QR valid
            if not payload.startswith("QR:"):
                return

            qr = payload[3:]

            ok, aksi, stats = ParkirModel.process_scan(qr)
            status = "VALID" if aksi == "masuk" else "INVALID"

            client.publish("ulbiparkir/gate/qr", status)
            print("📤 RESPON KE ESP:", status)

            socketio.emit("qr_update", {
                "waktu": datetime.now().strftime("%H:%M"),
                "status": status,
                "npm": qr,
                "nama": stats.get("nama", "-"),
                "durasi": "—"
            })

        socketio.emit("stats_update", stats)

    # ================= REGISTER =================
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()
