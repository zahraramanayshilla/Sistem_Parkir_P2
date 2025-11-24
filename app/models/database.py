import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Membuat koneksi ke PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            )
            print("Koneksi database berhasil!")
            return self.connection
        except Exception as e:
            print(f"Error koneksi database: {e}")
            return None

    def disconnect(self):
        """Menutup koneksi database"""
        if self.connection:
            self.connection.close()
            print("Koneksi database ditutup")


class DashboardModel:
    def __init__(self):
        self.db = Database()

    def get_all_users(self):
        """Mengambil semua data users"""
        conn = self.db.connect()
        if not conn:
            return []

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users ORDER BY id")
            users = cursor.fetchall()
            cursor.close()
            return users
        except Exception as e:
            print(f"Error mengambil data: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_user_by_id(self, user_id):
        """Mengambil user berdasarkan ID"""
        conn = self.db.connect()
        if not conn:
            return None

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            print(f"Error mengambil user: {e}")
            return None
        finally:
            self.db.disconnect()

    def create_user(self, name, email):
        """Menambah user baru"""
        conn = self.db.connect()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
                (name, email),
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            print(f"User baru ditambahkan dengan ID: {user_id}")
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error menambah user: {e}")
            return False
        finally:
            self.db.disconnect()

    def update_user(self, user_id, name, email):
        """Update data user"""
        conn = self.db.connect()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name = %s, email = %s WHERE id = %s",
                (name, email, user_id),
            )
            conn.commit()
            cursor.close()
            print(f"User ID {user_id} berhasil diupdate")
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error update user: {e}")
            return False
        finally:
            self.db.disconnect()

    def delete_user(self, user_id):
        """Hapus user"""
        conn = self.db.connect()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            print(f"User ID {user_id} berhasil dihapus")
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error hapus user: {e}")
            return False
        finally:
            self.db.disconnect()

    def get_statistics(self):
        """Mengambil statistik untuk dashboard"""
        conn = self.db.connect()
        if not conn:
            return {}

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            stats = cursor.fetchone()
            cursor.close()
            return stats
        except Exception as e:
            print(f"Error mengambil statistik: {e}")
            return {}
        finally:
            self.db.disconnect()
