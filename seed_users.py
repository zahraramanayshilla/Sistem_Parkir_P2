from werkzeug.security import generate_password_hash
from app import create_app
from app.models.db_models import User

app = create_app()
app.app_context().push()

def create_user(username, email, password, role):
    user = User.objects(username=username).first()
    if user:
        print(f"User {username} sudah ada dengan role {user.role}")
        return

    hashed = generate_password_hash(password)
    user = User(
        username=username,
        email=email,
        password=hashed,
        role=role,
    )
    user.save()
    print(f"User {username} dengan role {role} berhasil dibuat.")


if __name__ == "__main__":
    create_user("admin", "admin@kampus.com", "admin123", "admin")
    create_user("petugas1", "petugas1@kampus.com", "petugas123", "petugas")

