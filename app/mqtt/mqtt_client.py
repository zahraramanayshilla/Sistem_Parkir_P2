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

            # ======================
            # STATUS ESP (JANGAN MASUK DB)
            # ======================
            if payload == "READY":
                print("🟢 ESP ONLINE & READY")
                socketio.emit("qr_status", {"status": "READY"})
                return

            # ======================
            # ABAIKAN COMMAND ESP
            # ======================
            if payload.startswith(("LED", "BUZZER")):
                print("ℹ️ Command ESP diabaikan:", payload)
                return

            # Abaikan echo backend
            if payload in ("VALID", "INVALID"):
                return

            # ======================
            # HANYA TERIMA QR
            # ======================
            if not payload.startswith("QR:"):
                return

            # ======================
            # PARSING QR
            # ======================
            qr = payload[3:]
            qr_clean = qr.strip("{}")
            parts = qr_clean.split("|")

            if len(parts) != 3:
                socketio.emit("qr_status", {"status": "INVALID"})
                return

            nomor, npm, nama = parts

            # ======================
            # VALIDASI FORMAT QR
            # ======================
            is_valid = ParkirModel.validate_user(npm, nama)
            status = "VALID" if is_valid else "INVALID"

            client.publish(MQTT_TOPIC, status)

            socketio.emit("qr_status", {
                "status": status,
                "npm": npm,
                "nama": nama,
            })

            if not is_valid:
                return

            # ======================
        # PROSES PARKIR (MASUK / KELUAR)
        # ======================
        ok, aksi, result = ParkirModel.process_scan(
            nomor=nomor,
            npm=npm,
            nama=nama
        )

        if not ok:
            return

        # Ambil durasi dari hasil process_scan
        durasi = result.get("durasi", "—")

        # ======================
        # KIRIM KE DASHBOARD
        # ======================
        socketio.emit(
            "qr_update",
            {
                "waktu": datetime.now().strftime("%H:%M"),
                "status": aksi,        # MASUK / KELUAR
                "npm": npm,
                "nama": nama,
                "durasi": durasi,
            },
        )

        # ======================
        # UPDATE STATISTIK
        # ======================
        socketio.emit("stats_update", result)

    # ================= REGISTER =================
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()
