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
def generate_board(difficulty=0.5):
    seed = random.randint(0, 10000)
    puzzle = Sudoku(3, seed=seed).difficulty(difficulty)

    # convert back to string format
    cleaned_board = [
        [cell if cell is not None else 0 for cell in row]
        for row in puzzle.board
    ]
    str_puzzle = "".join("".join(str(num) for num in row) for row in cleaned_board)
    
    return str_puzzle

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

    print(puzzle)
    print(puzzle.has_multiple_solutions())
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