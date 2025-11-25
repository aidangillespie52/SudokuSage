# utils_board_encoding.py
import numpy as np
from board import Board

def board_to_string(board: Board) -> str:
    """Flatten Board._grid into a compact string like '530070000...'."""
    arr = board._grid  # shape (size, size)
    flat = arr.ravel()
    return "".join(str(int(v)) for v in flat)

def string_to_board(s: str, size: int, box_rows: int, box_cols: int) -> Board:
    """Create a Board from a compact string, e.g. length=81 for 9x9."""
    if len(s) != size * size:
        raise ValueError(f"Board string length {len(s)} != {size*size} for size {size}")
    nums = [int(ch) for ch in s]
    arr = np.array(nums, dtype=int).reshape(size, size)

    b = Board(size, box_cols, box_rows)
    b._grid = arr
    return b
