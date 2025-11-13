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
