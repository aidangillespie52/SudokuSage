# board.py

# imports
import numpy as np
import random

class Board:
    def __init__(self, size: int, box_cols: int, box_rows: int, fill=0):
        self._validate_init(size, box_rows, box_cols)
        
        self.size = size
        self.box_cols = box_cols
        self.box_rows = box_rows
        self.fill = fill
        self._grid = np.full((size, size), fill, dtype=int)
        self.num_cells = int((size / box_cols) * (size / box_rows))

    @staticmethod
    def _validate_init(size, box_rows, box_cols):
        # make sure its an actual board size
        if size <= 0:
            raise ValueError("size must be a positive integers")
        
        # ensure that boxes are proper
        if size % box_rows != 0:
            raise ValueError(f"size ({size}) must be divisible by box_rows ({box_rows})")
        if size % box_cols != 0:
            raise ValueError(f"size ({size}) must be divisible by box_cols ({box_cols})")

    def __getitem__(self, idx):
        return self._grid[idx]

    def __setitem__(self, idx, value):
        self._grid[idx] = value

    def __iter__(self):
        return iter(self._grid)

    def __str__(self):
        lines = []
        for r, row in enumerate(self._grid):
            # replace 0's with "."
            line = " ".join("." if v == 0 else str(v) for v in row)

            # vertical dividers
            parts = []
            for i in range(0, self.size, self.box_cols):
                parts.append(" ".join("." if v == 0 else str(v) for v in row[i:i+self.box_cols]))
            line = " | ".join(parts)

            lines.append(line)

            # horizontal dividers
            if (r + 1) % self.box_rows == 0 and (r + 1) < self.size:
                lines.append("-" * (self.size * 2 + (self.size // self.box_cols - 1) * 2))
        
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()

    def reset(self):
        self._grid.fill(self.fill)

    # just for testing purposes
    def random(self, no_empty=False):
        lower_bound = 0
        if no_empty:
            lower_bound = 1
            
        self._grid = np.random.randint(lower_bound, self.size, size=(self.size, self.size))
        
    # helper methods for rules logic
    def count_row(self, y, x):
        val = self._grid[y, x]
        return np.count_nonzero(self._grid[y, :] == val)

    def count_col(self, y, x):
        val = self._grid[y, x]
        return np.count_nonzero(self._grid[:, x] == val)

    def count_box(self, y, x):
        val = self._grid[y, x]
        
        box_y = (y // self.box_rows) * self.box_rows
        box_x = (x // self.box_cols) * self.box_cols
        box = self._grid[box_y:box_y+self.box_rows, box_x:box_x+self.box_cols]
        
        return np.count_nonzero(box == val)

    def is_valid(self):
        # check rows
        for y in range(self.size):
            row = self.get_row(y)
            filtered_row = row[row != 0]
            
            if len(set(filtered_row)) != len(filtered_row):
                return False
        
        # check cols
        for x in range(self.size):
            col = self.get_col(x)
            filtered_col = col[col != 0]
            
            if len(set(filtered_col)) != len(filtered_col):
                return False

        # check cells
        for z in range(self.num_cells):
            cell = self.get_cell(z)
            filtered_cell = cell[cell != 0]

            if len(set(filtered_cell)) != len(filtered_cell):
                return False

        return True
    
    def get_candidates(self):
        candidates = [[self.fill for _ in range(self.size)] for _ in range(self.size)]
        for (x, y), value in np.ndenumerate(self._grid):
            if value != 0:
                candidates[x][y] = [0]
            
            row = self.get_row(y)
            col = self.get_col(x)
            cell_idx,_ = self.board_index_to_cell_index(y,x)
            cell = self.get_cell(cell_idx)
                
            not_possible = np.union1d(np.union1d(row, col), cell)
            possible_values = np.setdiff1d(self.allowed_values(), not_possible)

            candidates[y][x] = possible_values
        
        return candidates
            
    def count_empty(self, arr: np.array) -> int:   return np.count_nonzero(arr == 0)
    def get_row(self, y: int):  return self._grid[y, :]
    def get_col(self, x: int):  return self._grid[:, x]
    def allowed_values(self):   return np.array(range(1, self.size + 1))
    def get_cell(self, idx: int):
        """
        Returns an array of values within queried cell. Cells are ordered from
        top left to bottom right.
        """
        if not (0 <= idx <= self.num_cells - 1):
            raise ValueError(f"cell {idx} is not valid")
        
        boxes_per_row = self.size // self.box_cols # number of boxes across

        box_row = idx // boxes_per_row             # which box row
        box_col = idx % boxes_per_row              # which box column

        r0 = box_row * self.box_rows
        r1 = r0 + self.box_rows
        c0 = box_col * self.box_cols
        c1 = c0 + self.box_cols

        return self._grid[r0:r1, c0:c1].copy().ravel()
    
    def cell_index_to_board_index(self, cell_idx: int, k: int):
        """
        Map index k (0..box_rows*box_cols-1) inside the raveled cell `cell_idx`
        to:
        - (r, c) on the whole board
        """
        if not (0 <= cell_idx < self.num_cells):
            raise ValueError("bad cell_idx")
        if not (0 <= k < self.box_rows * self.box_cols):
            raise ValueError("bad k")

        boxes_per_row = self.size // self.box_cols
        box_row = cell_idx // boxes_per_row
        box_col = cell_idx % boxes_per_row

        r0 = box_row * self.box_rows
        c0 = box_col * self.box_cols

        dr = k // self.box_cols
        dc = k % self.box_cols

        r = r0 + dr
        c = c0 + dc

        return (r, c)
    
    def board_index_to_cell_index(self, r: int, c: int):
        """
        Map (r, c) on the whole board to:
        - cell_idx (which 3x3 or box cell it's in)
        - k (index inside that cell's raveled view)
        """
        if not (0 <= r < self.size and 0 <= c < self.size):
            raise ValueError("bad board index")

        boxes_per_row = self.size // self.box_cols

        box_row = r // self.box_rows
        box_col = c // self.box_cols
        cell_idx = box_row * boxes_per_row + box_col

        dr = r % self.box_rows
        dc = c % self.box_cols
        k = dr * self.box_cols + dc

        return cell_idx, k

    def read_file(self, filepath):
        board = []
        
        with open(filepath, "r") as f:
            for line in f.readlines():
                row = []
                s = line.strip()
                
                for x in s:
                    row.append(int(x))

                board.append(row)
        
        self._grid = np.array(board)

if __name__ == '__main__':
    b = Board(9, 3, 3)
    b.random()