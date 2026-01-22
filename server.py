from flask import Flask, request, jsonify
import sqlite3
import threading

app = Flask(__name__)

DB_FILE = "users.db"
db_lock = threading.Lock()  # 🔒 защита от одновременной записи


def get_db():
    return sqlite3.connect(DB_FILE, timeout=10)


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        conn.commit()


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Пустые данные"}), 400

    with db_lock:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
            return jsonify({"status": "ok"}), 200

        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "Пользователь уже существует"}), 400

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    with db_lock:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = cursor.fetchone()

    if user:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "error", "message": "Неверный логин или пароль"}), 401


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
