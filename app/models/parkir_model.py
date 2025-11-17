import cv2

# =====================================================================
# ===========================kamera====================================
# =====================================================================
class CameraModel:
    def __init__(self, cam_id=0):
        self.cam = cv2.VideoCapture(cam_id)

    def get_frame(self):
        success, frame = self.cam.read()
        if not success:
            return None

        # Encode ke JPEG
        ret, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()

    def __del__(self):
        if self.cam.isOpened():
            self.cam.release()
# =====================================================================
# ===========================end kamera====================================
# =====================================================================

class ParkirModel:
    @staticmethod
    def get_dashboard_data():
        # Data dummy sementara (belum terhubung ke database)
        return {
            "total_slots": 100,
            "occupied_slots": 65,
            "available_slots": 35,
            "status": "Aktif",
        }
