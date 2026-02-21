from flask import Flask, render_template, request, redirect
from flask_cors import CORS
import sqlite3


# Import your existing blueprints
from routes.muscles import muscles_bp
from routes.exercises import exercises_bp
from routes.workouts import workouts_bp

app = Flask(__name__)
CORS(app)


DATABASE = "workout.db"


# -------------------------
# Database Connection
# -------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# HOME PAGE (FORM PAGE)
# -------------------------
@app.route("/")
def home():
    conn = get_db_connection()
    muscles = conn.execute("SELECT * FROM muscles ORDER BY id ASC").fetchall()
    conn.close()

    return render_template("add_workout.html", muscles=muscles)


# -------------------------
# SAVE WORKOUT (FORM POST)
# -------------------------
from flask import flash

app.secret_key = "supersecretkey"

@app.route("/save", methods=["POST"])
def save_workout():

    date = request.form["date"]
    muscle_id = request.form["muscle_id"]
    exercise_id = request.form["exercise_id"]

    # Get multiple reps & weight values
    reps_list = request.form.getlist("reps[]")
    weight_list = request.form.getlist("weight[]")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert main workout
    cursor.execute(
        "INSERT INTO workouts (date, muscle_id, exercise_id) VALUES (?, ?, ?)",
        (date, muscle_id, exercise_id),
    )

    workout_id = cursor.lastrowid

    # Insert sets
    for i in range(len(reps_list)):
        cursor.execute(
            """
            INSERT INTO workout_sets (workout_id, set_number, reps, weight)
            VALUES (?, ?, ?, ?)
            """,
            (workout_id, i + 1, reps_list[i], weight_list[i])
        )

    conn.commit()
    conn.close()

    flash("Workout Saved Successfully 💪🔥")
    return redirect("/")

# -------------------------
# WORKOUT HISTORY (GROUPED BY DATE)
# -------------------------
@app.route("/history")
def workout_history():

    conn = get_db_connection()

    workouts = conn.execute("""
        SELECT w.id, w.date, m.name AS muscle, e.name AS exercise
        FROM workouts w
        JOIN muscles m ON w.muscle_id = m.id
        JOIN exercises e ON w.exercise_id = e.id
        ORDER BY w.date DESC
    """).fetchall()

    history = {}

    for workout in workouts:
        workout_id = workout["id"]

        sets = conn.execute("""
            SELECT set_number, reps, weight
            FROM workout_sets
            WHERE workout_id = ?
        """, (workout_id,)).fetchall()

        date = workout["date"]

        if date not in history:
            history[date] = []

        history[date].append({
            "muscle": workout["muscle"],
            "exercise": workout["exercise"],
            "sets": sets
        })

    conn.close()

    return render_template("history.html", history=history)

# -------------------------
# REGISTER API BLUEPRINTS
# -------------------------
app.register_blueprint(muscles_bp, url_prefix="/muscles")
app.register_blueprint(exercises_bp, url_prefix="/exercises")
app.register_blueprint(workouts_bp, url_prefix="/workouts")


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)