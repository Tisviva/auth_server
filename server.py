from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "users.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "Auth server is running"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"error": "missing data"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (login, password) VALUES (?, ?)",
            (login, password)
        )
        conn.commit()
        return jsonify({"status": "registered"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "user exists"}), 409
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE login=? AND password=?",
        (login, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"error": "invalid credentials"}), 401
