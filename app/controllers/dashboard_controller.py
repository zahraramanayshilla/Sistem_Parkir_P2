from flask import Blueprint, render_template, Response
from app.models.parkir_model import ParkirModel
import cv2
import time

dashboard_bp = Blueprint("dashboard", __name__)
# Pakai VideoCapture aman
# =====================================================================
# ===========================kamera====================================
# =====================================================================
camera = None
camera_active = False  # 🔵 status kamera


def open_camera():
    """Membuka kamera hanya ketika dibutuhkan."""
    global camera, camera_active

    if camera_active:
        return True  # Kamera sudah aktif

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Camera failed to open")
        return False

    camera_active = True
    print("Camera started")
    return True


def close_camera():
    """Menutup kamera saat keluar dari section."""
    global camera, camera_active
    if camera_active and camera is not None:
        camera.release()
        camera = None
        camera_active = False
        print("Camera stopped")


def generate_camera():
    """Generator stream MJPEG."""
    global camera

    while camera_active:
        if camera is None:
            break

        success, frame = camera.read()
        if not success:
            continue

        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )
        time.sleep(0.03)


@dashboard_bp.route("/camera/start")
def start_camera():
    if open_camera():
        return {"status": "started"}
    return {"status": "failed"}, 500


@dashboard_bp.route("/camera/stop")
def stop_camera():
    close_camera()
    return {"status": "stopped"}


@dashboard_bp.route("/camera")
def camera_stream():
    if not camera_active:
        open_camera()

    return Response(
        generate_camera(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@dashboard_bp.route("/camera")
def camera_feed():
    return Response(
        generate_camera(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )
# =====================================================================
# ===========================end kamera====================================
# =====================================================================

@dashboard_bp.route("/")
def index():
    data = ParkirModel.get_dashboard_data()
    return render_template("index.html", data=data)


@dashboard_bp.route("/login")
def login():
    return render_template("login.html")
