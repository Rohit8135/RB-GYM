from flask import Blueprint, jsonify
import sqlite3

exercises_bp = Blueprint("exercises", __name__)

DATABASE = "workout.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@exercises_bp.route("/<int:muscle_id>", methods=["GET"])
def get_exercises(muscle_id):
    conn = get_db_connection()
    exercises = conn.execute(
        "SELECT * FROM exercises WHERE muscle_id = ?",
        (muscle_id,)
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in exercises])