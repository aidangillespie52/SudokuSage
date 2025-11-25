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
            puzzle_id     INTEGER NOT NULL,
            step_number   INTEGER NOT NULL,
            hint_text     TEXT,
            x             INTEGER,      -- 1-based
            y             INTEGER,      -- 1-based
            value         INTEGER,
            board_before  TEXT NOT NULL,
            board_after   TEXT NOT NULL,
            method_used   TEXT,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (puzzle_id) REFERENCES puzzles(id)
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

def log_step(
    puzzle_id: int,
    step_number: int,
    hint_text: str,
    x: int,
    y: int,
    value: int,
    board_before: str,
    board_after: str,
    method_used: str = "LLM"
) -> int:
    """Insert a solve step and return its ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO solve_steps
        (puzzle_id, step_number, hint_text, x, y, value,
         board_before, board_after, method_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (puzzle_id, step_number, hint_text, x, y, value,
         board_before, board_after, method_used),
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
