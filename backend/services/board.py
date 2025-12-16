# backend/services/board.py

# imports
import random
from sudoku import Sudoku
from fastapi import HTTPException

# local imports
from backend.utils import get_logger

MIN_VALID = 0.0     # 0% empty (easiest)
MAX_VALID = 0.79    # theoretical max — you can choose 0.79 if you want unique solution
logger = get_logger(__name__)

# validate difficulty param
def validate_difficulty(difficulty: float) -> None:
    # validate difficulty
    if difficulty < MIN_VALID or difficulty > MAX_VALID:
        logger.warning(f"Invalid difficulty requested: {difficulty}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid difficulty {difficulty}. Must be between {MIN_VALID} and {MAX_VALID}."
        )

    random.seed(random.randint(0, 10000)) # added because it was generating the same board on each request
    
# generate a sudoku board with given difficulty
def generate_board(difficulty=0.5) -> str:
    seed = random.randint(0, 10000)
    puzzle = Sudoku(3, seed=seed).difficulty(difficulty)

    # convert back to string format
    cleaned_board = [
        [cell if cell is not None else 0 for cell in row]
        for row in puzzle.board
    ]
    str_puzzle = "".join("".join(str(num) for num in row) for row in cleaned_board)
    
    return str_puzzle

def count_empties(board) -> int:
    return sum(1 for row in board for v in row if (v is None or v == 0))

def empties_to_pysudoku_difficulty(empties: int, *, board_size: int = 81) -> float:
    if not (0 <= empties <= board_size):
        raise ValueError(f"empties must be in [0, {board_size}]")
    return empties / board_size

def puzzle_to_str(pzl: Sudoku) -> str:
    cleaned_board = [
        [cell if cell is not None else 0 for cell in row]
        for row in pzl.board
    ]

    str_solution = "".join("".join(str(num) for num in row) for row in cleaned_board)
    return str_solution

# TODO: split this into two different functions where we solve and return sudoku board instead of str
# solve a sudoku board given in string format
def solve_board(board_str):
    # make rows
    board = []
    for i in range(9):
        row = [board_str[x] for x in range(i*9, (i+1)*9)]
        board.append([int(num) if num != '0' else None for num in row])
    
    puzzle = Sudoku(3)
    puzzle.board = board
    puzzle = puzzle.solve()

    if puzzle is None:
        raise ValueError("Invalid board string; cannot be solved.")

    cleaned_board = [
        [cell if cell is not None else 0 for cell in row]
        for row in puzzle.board
    ]

    str_solution = "".join("".join(str(num) for num in row) for row in cleaned_board)
    return str_solution

# for testing
if __name__ == "__main__":
    b = generate_board(0.5)
    solve_board(b)