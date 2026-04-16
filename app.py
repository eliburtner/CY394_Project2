from flask import Flask, jsonify, request
import mysql.connector
from db import get_db, init_app

app = Flask(__name__)
init_app(app)

@app.route("/")
def home():
    return "Flask backend is running"

@app.route("/tables")
def tables():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tables;")
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)

@app.route("/available-tables")
def available_tables():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tables WHERE available_seats > 0;")
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)

@app.route("/update-seats", methods=["POST"])
def update_seats():
    data = request.get_json()

    table_id = data.get("table_id")
    user_id = data.get("user_id")
    available_seats = data.get("available_seats")

    if table_id is None or user_id is None or available_seats is None:
        return jsonify({"error": "table_id, user_id, and available_seats are required"}), 400

    if available_seats < 0:
        return jsonify({"error": "available_seats cannot be negative"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tables WHERE table_id = %s", (table_id,))
    table = cursor.fetchone()

    if table is None:
        cursor.close()
        return jsonify({"error": "table not found"}), 404

    if table["user_id"] != user_id:
        cursor.close()
        return jsonify({"error": "user is not authorized to update this table"}), 403

    cursor.execute(
        "UPDATE tables SET available_seats = %s WHERE table_id = %s",
        (available_seats, table_id)
    )
    db.commit()

    cursor.execute("SELECT * FROM tables WHERE table_id = %s", (table_id,))
    updated_table = cursor.fetchone()
    cursor.close()

    return jsonify({
        "message": "available seats updated successfully",
        "table": updated_table
    }), 200

@app.route("/claim-seat", methods=["POST"])
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

        cursor.execute("SELECT * FROM tables WHERE table_id = %s", (table_id,))
        table = cursor.fetchone()
        if table is None:
            return jsonify({"error": "table not found"}), 404

        cursor.execute("SELECT * FROM claims WHERE user_id = %s", (user_id,))
        existing_claim = cursor.fetchone()
        if existing_claim is not None:
            return jsonify({"error": "user has already claimed a seat"}), 400

        cursor.execute(
            "UPDATE tables SET available_seats = available_seats - 1 WHERE table_id = %s AND available_seats > 0",
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

@app.route("/reset-meal", methods=["POST"])
def reset_meal():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM claims;")
        cursor.execute("UPDATE tables SET available_seats = 0;")
        db.commit()

        return jsonify({
            "message": "meal reset successfully"
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)