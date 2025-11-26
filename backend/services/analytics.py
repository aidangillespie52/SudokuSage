# backend/services/analytics.py

# imports
from typing import List, Dict, Any

# local imports
from backend.database import db_driver as driver

# gets all solve steps from the database
def get_solve_steps() -> List[Dict[str, Any]]:
    conn = driver.get_connection()  # use YOUR driver function
    cur = conn.cursor()

    cur.execute("SELECT id, puzzle, session_id, step_number, hint_text, r, c, value, method_used, created_at FROM solve_steps ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()

    # convert to JSON
    return [
        {
            "id": r[0], "puzzle": r[1], "session_id": r[2],
            "step_number": r[3], "hint_text": r[4],
            "r": r[5], "c": r[6], "value": r[7],
            "method_used": r[8], "created_at": r[9]
        }
        for r in rows
    ]