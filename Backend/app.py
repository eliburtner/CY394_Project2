from flask import Flask, request, redirect, render_template, session, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import mysql.connector
import re
from db import get_db, init_app

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key' # Required for session support

CORS(app)
init_app(app)

# Initalize SocketIO with Flask app
# async_mode determines the underlying async framework
socketio = SocketIO(
    app,
    cors_allowed_origins="*", # Allow all origins (configure for production)
    async_mode='eventlet', # Use eventlet for async (alternatives: gevent, threading)
    ping_timeout=60, # Seconds before considering connection dead
    ping_interval=25 # Seconds between ping packets
)

@app.route("/")
def home():
    return "Flask backend is running"

@socketio.on("connect")
def handle_connect():
    print(f"Client connect: {request.sid}")
    emit("server_message", {"message": "Connected to SeatScout WebSocket"})

@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    table_num = data.get("table_num")

    if not username or not password or not role:
        return jsonify({"error": "username, password, and role are required"}), 400

    if role not in ["Floater", "Table Commandant"]:
        return jsonify({"error": "role must be 'Floater', 'Table Commandant', or 'Admin'"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user is not None:
            return jsonify({"error": "username already exists"}), 400
        
        table_id = None

        if role == "Table Commandant":
            if table_num is None or str(table_num).strip() == "":
                return jsonify({"error": "table_num is required for Table Commandant"}), 400
            table_num = str(table_num).strip().upper()
            if not re.match(r"^\d+[A-F]$", table_num):
                return jsonify({"error": "table_num must end with a capital letter A-F, like 1A or 12F"}), 400
            cursor.execute("SELECT * FROM tables WHERE table_num = %s", (table_num,))
            existing_table = cursor.fetchone()

            if existing_table is not None:
                return jsonify({"error": "that table number is already registered"}), 400

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )

        user_id = cursor.lastrowid
        table_id = None

        if role == "Table Commandant":
            cursor.execute(
                "INSERT INTO tables (table_num, user_id, available_seats) VALUES (%s, %s, %s)",
                (table_num, user_id, 0)
            )
            table_id = cursor.lastrowid

        db.commit()

        return jsonify({
            "message": "Registration successful",
            "user_id": user_id,
            "username": username,
            "role": role,
            "table_id": table_id,
            "table_num": table_num if role == "Table Commandant" else None
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cursor.fetchone()

        if user is None:
            return jsonify({"error": "invalid username or password"}), 401

        response = {
            "message": "login successful",
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"]
        }

        if user["role"] == "Table Commandant":
            cursor.execute(
                "SELECT table_id, table_num FROM tables WHERE user_id = %s",
                (user["user_id"],)
            )
            table = cursor.fetchone()

            if table is not None:
                response["table_id"] = table["table_id"]
                response["table_num"] = table["table_num"]

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


@app.route("/api/tables")
def tables():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT table_id, table_num, available_seats FROM tables")
        rows = cursor.fetchall()
        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


@app.route("/api/claim-seat", methods=["POST"])
def claim_seat():
    data = request.get_json()

    user_id = data.get("user_id")
    table_id = data.get("table_id")

    if user_id is None or table_id is None:
        return jsonify({"error": "user_id and table_id are required"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "user not found"}), 404

        if user["role"] != "Floater":
            return jsonify({"error": "only floaters can claim seats"}), 403

        cursor.execute("SELECT * FROM claims WHERE user_id = %s", (user_id,))
        existing_claim = cursor.fetchone()
        if existing_claim is not None:
            return jsonify({"error": "user has already claimed a seat"}), 400

        cursor.execute("SELECT * FROM tables WHERE table_id = %s", (table_id,))
        table = cursor.fetchone()
        if table is None:
            return jsonify({"error": "table not found"}), 404

        cursor.execute(
            "UPDATE tables SET available_seats = available_seats - 1 "
            "WHERE table_id = %s AND available_seats > 0",
            (table_id,)
        )

        if cursor.rowcount == 0:
            db.rollback()
            return jsonify({"error": "no available seats at this table"}), 400

        cursor.execute(
            "INSERT INTO claims (user_id, table_id) VALUES (%s, %s)",
            (user_id, table_id)
        )

        db.commit()

        cursor.execute(
            "SELECT table_id, table_num, available_seats FROM tables WHERE table_id = %s",
            (table_id,)
        )

        updated_table = cursor.fetchone()

        socketio.emit("seat_update", updated_table)

        return jsonify({
            "message": "seat claimed successfully",
            "user_id": user_id,
            "table_id": table_id
        }), 200

    except mysql.connector.IntegrityError:
        db.rollback()
        return jsonify({"error": "claim could not be completed"}), 400

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


@app.route("/api/update-seats", methods=["POST"])
def update_seats():
    data = request.get_json()

    table_id = data.get("table_id")
    user_id = data.get("user_id")
    available_seats = data.get("available_seats")

    if table_id is None or user_id is None or available_seats is None:
        return jsonify({"error": "table_id, user_id, and available_seats are required"}), 400

    try:
        available_seats = int(available_seats)
    except ValueError:
        return jsonify({"error": "available_seats must be an integer"}), 400

    if available_seats < 0:
        return jsonify({"error": "available_seats cannot be negative"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({"error": "user not found"}), 404

        if user["role"] != "Table Commandant":
            return jsonify({"error": "only Table Commandants can update seats"}), 403

        cursor.execute(
            "SELECT * FROM tables WHERE table_id = %s AND user_id = %s",
            (table_id, user_id)
        )
        table = cursor.fetchone()

        if table is None:
            return jsonify({"error": "this table is not assigned to this commandant"}), 403

        cursor.execute(
            "UPDATE tables SET available_seats = %s WHERE table_id = %s",
            (available_seats, table_id)
        )

        updated_table = {
            "table_id": table_id,
            "table_num": table["table_num"],
            "available_seats": available_seats
        }

        db.commit()

        socketio.emit("seat_update", updated_table)

        return jsonify({
            "message": "available seats updated successfully",
            "table_id": table_id,
            "available_seats": available_seats
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()

if __name__ == "__main__":
    # Use socketio.run() instead of app.run() for WebSocket support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)