from flask import Blueprint, jsonify
from models.db import get_db_connection

muscles_bp = Blueprint("muscles", __name__)

@muscles_bp.route("/", methods=["GET"])
def get_muscles():
    conn = get_db_connection()
    muscles = conn.execute("SELECT * FROM muscles").fetchall()
    conn.close()
    return jsonify([dict(row) for row in muscles])