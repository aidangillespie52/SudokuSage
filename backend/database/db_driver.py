#driver program for the sql database

# db.py
from pathlib import Path
import sqlite3
from typing import Optional, List, Tuple

DB_PATH = Path(__file__).resolve().parent / "sudoku.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # nice dict-like rows
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    # puzzles table: one row per puzzle
    cur.execute("""
        CREATE TABLE IF NOT EXISTS puzzles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            size        INTEGER NOT NULL,
            box_rows    INTEGER NOT NULL,
            box_cols    INTEGER NOT NULL,
            initial_board TEXT NOT NULL
        )
    """)

    # solve_steps: one row per hint/move
    cur.execute("""
        CREATE TABLE IF NOT EXISTS solve_steps (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle        INTEGER NOT NULL,
            session_id    TEXT NOT NULL,
            step_number   INTEGER NOT NULL,
            hint_text     TEXT,
            r             INTEGER,      -- 1-based
            c             INTEGER,      -- 1-based
            value         INTEGER,      -- digit placed
            method_used   TEXT,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (puzzle) REFERENCES puzzles(initial_board)
        )
    """)

    conn.commit()
    conn.close()

def create_puzzle(size: int, box_rows: int, box_cols: int, initial_board_str: str) -> int:
    """Insert a new puzzle and return its ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO puzzles (size, box_rows, box_cols, initial_board)
        VALUES (?, ?, ?, ?)
        """,
        (size, box_rows, box_cols, initial_board_str),
    )
    
    conn.commit()
    puzzle_id = cur.lastrowid
    conn.close()
    return puzzle_id

def _get_next_step_number(conn: sqlite3.Connection, puzzle: str) -> int:
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(step_number) AS max_step FROM solve_steps WHERE puzzle = ?",
        (puzzle,),
    )
    row = cur.fetchone()
    max_step = row["max_step"] if row and row["max_step"] is not None else None
    return 0 if max_step is None else max_step + 1

def log_step(
    puzzle: int,
    session_id: str,
    hint_text: str,
    r: int,
    c: int,
    value: int,
    method_used: str = "Unknown",
    step_number: Optional[int] = None,
) -> int:
    """Insert a solve step and return its ID."""
    
    conn = get_connection()
    cur = conn.cursor()
    
    if step_number is None:
        step_number = _get_next_step_number(conn, puzzle)

    cur.execute(
        """
        INSERT INTO solve_steps
        (puzzle, session_id, step_number, hint_text, r, c, value,
         method_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (puzzle, session_id, step_number, hint_text, r, c, value,
         method_used),
    )
    
    conn.commit()
    step_id = cur.lastrowid
    conn.close()
    
    return step_id

def get_steps_for_puzzle(puzzle_id: int) -> List[sqlite3.Row]:
    """Fetch all steps for a puzzle in order."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM solve_steps WHERE puzzle_id=? ORDER BY step_number ASC",
        (puzzle_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    id = "some-id"
    
    rows = get_steps_for_puzzle(id)
    print(rows)