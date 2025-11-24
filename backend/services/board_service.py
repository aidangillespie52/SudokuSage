import random
from sudoku import Sudoku

def generate_board(difficulty=0.5):
    seed = random.randint(0, 10000)
    puzzle = Sudoku(3, seed=seed).difficulty(difficulty)

    cleaned_board = [
        [cell if cell is not None else 0 for cell in row]
        for row in puzzle.board
    ]

    str_puzzle = "".join("".join(str(num) for num in row) for row in cleaned_board)
    return str_puzzle

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

if __name__ == "__main__":
    b = generate_board(0.5)
    solve_board(b)