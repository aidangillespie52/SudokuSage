// frontend/static/js/board.js

// TODO: make it to where you can add change numbers while selecting a number you've edited
window.BoardUtils = (function () {
    function countEmptySquares(boardStr) {
        return boardStr.split("").filter(ch => ch === "0").length;
    }

    function validateBoardString(boardStr) {
    if (boardStr.length !== 81) {
        throw new Error("Board string must be exactly 81 characters");
    }

    // convert to 2D array of ints
    const board = [];
    for (let r = 0; r < 9; r++) {
        const row = [];
        for (let c = 0; c < 9; c++) {
        const ch = boardStr[r * 9 + c];
        row.push(ch === "0" ? 0 : Number(ch));
        }
        board.push(row);
    }

    const errors = {
        rows: new Set(),     // indices of bad rows
        cols: new Set(),     // indices of bad cols
        boxes: new Set(),    // indices 0–8 for the 3x3 boxes
    };

    function hasDuplicateNonZero(nums) {
        const seen = new Set();
        for (const n of nums) {
        if (n === 0) continue;
        if (seen.has(n)) return true;
        seen.add(n);
        }
        return false;
    }

    // check rows
    for (let r = 0; r < 9; r++) {
        if (hasDuplicateNonZero(board[r])) {
        errors.rows.add(r);
        }
    }

    // check columns
    for (let c = 0; c < 9; c++) {
        const col = [];
        for (let r = 0; r < 9; r++) col.push(board[r][c]);
        if (hasDuplicateNonZero(col)) {
        errors.cols.add(c);
        }
    }

    // check 3x3 boxes
    // box index: br*3 + bc, where br,bc in 0..2
    for (let br = 0; br < 3; br++) {
        for (let bc = 0; bc < 3; bc++) {
        const nums = [];
        for (let r = br * 3; r < br * 3 + 3; r++) {
            for (let c = bc * 3; c < bc * 3 + 3; c++) {
            nums.push(board[r][c]);
            }
        }
        if (hasDuplicateNonZero(nums)) {
            const boxIndex = br * 3 + bc;
            errors.boxes.add(boxIndex);
        }
        }
    }

    const valid =
        errors.rows.size === 0 &&
        errors.cols.size === 0 &&
        errors.boxes.size === 0;

    // convert Sets to arrays for easier JSON / usage
    return {
        valid,
        rows: Array.from(errors.rows),
        cols: Array.from(errors.cols),
        boxes: Array.from(errors.boxes),
    };
    }

    function onBoardChanged() {
        console.log("Board changed!");
        const boardString = getBoardString();
        const result = validateBoardString(boardString);

        console.log(result.valid);  // true/false
        console.log("Bad rows:", result.rows);
        console.log("Bad cols:", result.cols);
        console.log("Bad boxes:", result.boxes);

        console.log(boardString);
    }

    function getBoardString() {
        const boardEl = document.getElementById('board');
        const inputs = boardEl.querySelectorAll(".cell input");
        let out = "";

        inputs.forEach(input => {
            const val = input.value.trim();
            out += val === "" ? "0" : val;
        });

        return out;
    }

    function buildGrid(puzzle, boardEl) {
        boardEl.innerHTML = '';
        
        // Build 9×9 grid
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
            const idx = r * 9 + c;
            const v = puzzle[idx];
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = String(r);
            cell.dataset.col = String(c);
            cell.setAttribute('role', 'gridcell');

            const input = document.createElement('input');
            input.inputMode = 'numeric';
            input.autocomplete = 'off';
            input.maxLength = 1;
            input.ariaLabel = `Row ${r + 1} column ${c + 1}`;
            input.placeholder = '';
            
            input.addEventListener("input", () => {
                onBoardChanged();
            });

            if (v !== '0') {
                input.value = v;
                cell.dataset.given = 'true';
                input.readOnly = true;
                input.tabIndex = -1;
            } else {
                input.tabIndex = 0;
                input.addEventListener('beforeinput', (e) => {
                if (e.data && !/[1-9]/.test(e.data)) e.preventDefault();
                });
                input.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/[^1-9]/g, '').slice(-1);
                });
                input.addEventListener('keydown', (e) => {
                const key = e.key;
                if (!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(key)) return;
                e.preventDefault();
                let nr = r, nc = c;
                if (key === 'ArrowUp') nr = Math.max(0, r - 1);
                if (key === 'ArrowDown') nr = Math.min(8, r + 1);
                if (key === 'ArrowLeft') nc = Math.max(0, c - 1);
                if (key === 'ArrowRight') nc = Math.min(8, c + 1);
                const next = boardEl.querySelector(
                    `.cell[data-row="${nr}"][data-col="${nc}"] input:not([readonly])`
                ) || boardEl.querySelector(`.cell[data-row="${nr}"][data-col="${nc}"] input`);
                next?.focus();
                });
            };

            cell.appendChild(input);
            boardEl.appendChild(cell);
            }
        }
    }

    function createBoard(difficulty=0.5) {
        const boardEl = document.getElementById('board');
        let puzzle;
        
        fetch(`/board/new/${difficulty}`, {
            method: "POST"
        }).then(response => response.json()).then(data => {
            console.log("New board created:", data);
            puzzle = data;
        }).then(() => {
            buildGrid(puzzle, boardEl);
            
            // Count empties
            const emptyCount = countEmptySquares(puzzle);
            console.log("Empty squares:", emptyCount);
        });
    }

    // --- expose these functions ---
    return {
        validateBoardString,
        onBoardChanged,
        getBoardString,
        buildGrid,
        createBoard
    };

})();

const newGameBtn = document.getElementById("btn-new-game");
const modal = document.getElementById("difficulty-modal");
const cancelBtn = document.getElementById("difficulty-cancel");

// Open difficulty popup ONLY when New Game pressed
newGameBtn.addEventListener("click", () => {
  modal.classList.remove("hidden");
});

// Close popup helper
function closeModal() {
  modal.classList.add("hidden");
}

// Cancel button closes it
cancelBtn.addEventListener("click", closeModal);

// Click outside card closes it
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeModal();
});

// ESC closes it
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});


// Difficulty buttons → run game & hide popup
document.querySelectorAll(".difficulty-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const diff = btn.dataset.diff;

    const strengthMap = {
      "very-easy": 0.10,
      "easy":      0.25,
      "medium":    0.50,
      "hard":      0.75,
      "expert":    0.90
    };

    const strength = strengthMap[diff];

    console.log("selected difficulty:", diff, "strength:", strength);

    closeModal();

    // 🔥 Create the board with 0–1 difficulty selection
    window.BoardUtils.createBoard(strength);
  });
});



window.BoardUtils.createBoard(0.5);