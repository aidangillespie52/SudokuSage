# backend/api/board.py

# imports
from random import random
from fastapi import APIRouter, HTTPException

# local imports
from backend.database.db_driver import create_puzzle
from backend.services.board import generate_board, validate_difficulty
from backend.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/board")

# difficulty constraints for a 9×9 Sudoku
MIN_VALID = 0.0     # 0% empty (easiest)
MAX_VALID = 0.79    # theoretical max — you can choose 0.79 if you want unique solution

@router.post("/new/{difficulty}")
async def get_board(difficulty: float) -> str:
    try:
        validate_difficulty(difficulty)
    except HTTPException as e:
        raise e
    
    try:
        board = generate_board(difficulty)
    except Exception as e:
        logger.exception("Board generation failed.")
        raise HTTPException(status_code=500, detail="Failed to generate board.")
    
    # store the generated puzzle in the SQLite database.
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

