# rules.py

# imports
from dataclasses import dataclass
from typing import Tuple
import numpy as np
from board import Board
from typing import Optional
from itertools import product

@dataclass
class Result:
    idx: Tuple[int, int]
    value: int

def find_single_candidates(bd: Board) -> Optional[Result]:
    cds = bd.get_candidates()
    pairs = product(range(bd.size), range(bd.size))
    
    for x,y in pairs:
        if bd[x,y] != 0:
            continue
        
        possible_vals = cds[x][y] 
        
        if len(possible_vals) != 1:
            continue
        return Result((x,y), possible_vals[0])
    
    return None


# TODO: to where it returns a new board rather than a solved board
def solve(b):
    r = True
    i = 0
    while r:
        i += 1
        r = find_single_candidates(b)
        x,y = r.idx
        b[x,y] = r.value
        
        if b.count_empty(b._grid) == 0:
            print("\n")
            print(f"SOLVED!\n")
            print(b)
            break
    
    
    

