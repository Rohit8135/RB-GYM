from flask import Blueprint, request, jsonify
from models.db import get_db_connection

workouts_bp = Blueprint("workouts", __name__)

@workouts_bp.route("/", methods=["POST"])
def create_workout():
    data = request.json

    date = data["date"]
    muscle_id = data["muscle_id"]
    exercise_id = data["exercise_id"]
    sets = data["sets"]  # list of {reps, weight}

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert into workouts table
    cursor.execute(
        "INSERT INTO workouts (date, muscle_id, exercise_id) VALUES (?, ?, ?)",
        (date, muscle_id, exercise_id)
    )

    workout_id = cursor.lastrowid

    # Insert sets
    for index, s in enumerate(sets):
        cursor.execute(
            """
            INSERT INTO workout_sets (workout_id, set_number, reps, weight)
            VALUES (?, ?, ?, ?)
            """,
            (workout_id, index + 1, s["reps"], s["weight"])
        )

    conn.commit()
    conn.close()

    return jsonify({"message": "Workout saved successfully"})