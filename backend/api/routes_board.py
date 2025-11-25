# backend/api/routes_ai.py

from random import random
from fastapi import APIRouter, HTTPException
from backend.utils import get_logger
from backend.services.board_service import generate_board, solve_board
import random

from backend.database.db_driver import create_puzzle

logger = get_logger(__name__)
router = APIRouter(prefix="/board")

# Difficulty constraints for a 9×9 Sudoku
MIN_VALID = 0.0    # 0% empty (easiest)
MAX_VALID = 1.0    # 100% empty (theoretical max — you can choose 0.79 if you want "unique solution" max)

@router.post("/new/{difficulty}")
async def get_board(difficulty: float):
    # validate difficulty
    if difficulty < MIN_VALID or difficulty > MAX_VALID:
        logger.warning(f"Invalid difficulty requested: {difficulty}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid difficulty {difficulty}. Must be between {MIN_VALID} and {MAX_VALID}."
        )

    random.seed(random.randint(0, 10000)) # added because it was generating the same board on each request
    
    try:
        board = generate_board(difficulty)
    except Exception as e:
        logger.exception("Board generation failed.")
        raise HTTPException(status_code=500, detail="Failed to generate board.")
    
    # Store the generated puzzle in the SQLite database.
    # 9x9 Sudoku => size=9, box_rows=3, box_cols=3.
    try:
        create_puzzle(
            size=9,
            box_rows=3,
            box_cols=3,
            initial_board_str=board,
        )
    except Exception:
        logger.exception("Failed to persist generated puzzle to the database.")
    
    return board

