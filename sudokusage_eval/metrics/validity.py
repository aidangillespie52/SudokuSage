# sudokusage-eval/metrics/validity.py

def is_valid_solution(proposed_board: str, solved_board: str):
    for proposed_cell, solved_cell in zip(proposed_board, solved_board):
        if proposed_cell == "0":
            continue
        
        if proposed_cell != solved_cell:
            return False
    
    return True