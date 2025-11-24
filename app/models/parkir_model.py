from app import db


class ParkirModel:
    @staticmethod
    def check_username_exists(username):
        result = db.session.execute(
            "SELECT id FROM users WHERE username = :username", {"username": username}
        ).fetchone()
        return result is not None

    @staticmethod
    def register_user(username, password, email, full_name):
        try:
            db.session.execute(
                "INSERT INTO users (username, password, email, full_name) VALUES (:username, :password, :email, :full_name)",
                {
                    "username": username,
                    "password": password,
                    "email": email,
                    "full_name": full_name,
                },
            )
            db.session.commit()
            return True
        except Exception as e:
            print("Error register_user:", e)
            db.session.rollback()
            return False

    @staticmethod
    def validate_login(username, password):
        user = db.session.execute(
            "SELECT * FROM users WHERE username = :username AND password = :password",
            {"username": username, "password": password},
        ).fetchone()
        if user:
            return dict(user)
        return None
