import paho.mqtt.client as mqtt
from datetime import datetime

from app.models.parkir_model import ParkirModel
from app.controllers.socket_controller import socketio

# ================= MQTT TOPIC =================
MQTT_TOPIC_QR = "ulbiparkir/gate/qr"
MQTT_TOPIC_RESPON = "ulbiparkir/gate/respon"


last_qr = {}
DUPLICATE_WINDOW = 3  # detik 


def start_mqtt(app):
    client = mqtt.Client(client_id="flask-parkir-backend")

    # ================= CONNECT =================
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT CONNECTED")
            client.subscribe(MQTT_TOPIC_QR)
        else:
            print("❌ MQTT FAILED, rc =", rc)

    # ================= MESSAGE =================
    def on_message(client, userdata, msg):
        with app.app_context():
            payload = msg.payload.decode().strip()
            now = datetime.now() 
            print("📥 MQTT MASUK:", payload)

            # ⬅️ (PERUBAHAN) timeout scan
            if payload == "SCAN_TIMEOUT":
                socketio.emit(
                    "qr_status",
                    {
                        "status": "TIMEOUT",
                        "message": "QR tidak terdeteksi selama 15 detik",
                    },
                )
                return

            # =================================================
            # 1️⃣ STATUS ESP (TETAP DIPERTAHANKAN)
            # =================================================
            if payload == "READY":
                print("🟢 ESP ONLINE & READY")
                socketio.emit("qr_status", {"status": "READY"})
                return

            # =================================================
            # 2️⃣ ABAIKAN COMMAND INTERNAL ESP (TETAP)
            # =================================================
            if payload.startswith(("LED", "BUZZER")):
                print("ℹ️ Command ESP diabaikan:", payload)
                return

            # =================================================
            # 3️⃣ SEMUA SELAIN QR → INVALID (BARU, TAPI AMAN)
            # =================================================
            if not payload.startswith("QR:"):
                print("❌ Payload bukan QR resmi")
                client.publish(MQTT_TOPIC_RESPON, "INVALID")
                return

            # ✅ DEDUP YANG BENAR
            last_time = last_qr.get(payload)
            if last_time and (now - last_time).total_seconds() < DUPLICATE_WINDOW:
                print("⏱️ Duplikat QR diabaikan")
                return

            last_qr[payload] = now
                
            # =================================================
            # 4️⃣ PARSING QR (TETAP)
            # FORMAT: QR:{nomor|npm|nama}
            # =================================================
            qr_clean = payload[3:].strip("{}")
            parts = qr_clean.split("|")

            if len(parts) != 3:
                print("❌ Format QR salah")
                client.publish(MQTT_TOPIC_RESPON, "INVALID")
                socketio.emit("qr_status", {"status": "INVALID"})
                return

            nomor, npm, nama = parts

            # =================================================
            # 5️⃣ VALIDASI USER (TETAP)
            # =================================================
            if not ParkirModel.validate_user(npm, nama):
                print("❌ User tidak terdaftar")
                client.publish(MQTT_TOPIC_RESPON, "INVALID")
                socketio.emit(
                    "qr_status", {"status": "INVALID", "npm": npm, "nama": nama}
                )
                return

            # =================================================
            # 6️⃣ PROSES PARKIR (TETAP)
            # =================================================
            ok, aksi, result = ParkirModel.process_scan(nomor, npm, nama)
            if not ok:
                client.publish(MQTT_TOPIC_RESPON, "INVALID")
                return

            durasi = result.get("durasi", "—")

            client.publish(MQTT_TOPIC_RESPON, "VALID")

            socketio.emit(
                "qr_status",
                {
                    "status": "VALID",
                    "aksi": aksi,
                    "npm": npm,
                    "nama": nama,
                    "durasi": durasi,
                },
            )

            socketio.emit(
                "qr_update",
                {
                    "waktu": datetime.now().strftime("%H:%M"),
                    "status": aksi,
                    "npm": npm,
                    "nama": nama,
                    "durasi": durasi,
                },
            )

            socketio.emit("parkir_stats", result)

    # ================= REGISTER =================
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()
