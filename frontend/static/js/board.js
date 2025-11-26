// frontend/static/js/board.js

let puzzle_id = null;  // will be set when a new puzzle is created

let timerInterval = null;
let startTime = null;
let currentDifficulty = 0.5;

function startTimer() {
    const timerEl = document.getElementById("timer");
    if (!timerEl) return;

    // clear any old timer
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    startTime = Date.now();
    timerEl.textContent = "00:00";

    timerInterval = setInterval(() => {
        const diffMs = Date.now() - startTime;
        const totalSeconds = Math.floor(diffMs / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        timerEl.textContent =
            String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function clearChat() {
  messages = [];
  const windowEl = document.getElementById("response-window");
  windowEl.innerHTML = "";
}

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
            rows: new Set(),
            cols: new Set(),
            boxes: new Set(),
        };

        // store exact conflicting cells as "r,c" strings
        const conflictSet = new Set();

        function markDuplicatesInRow(r) {
            const map = new Map(); // value -> [cols...]
            for (let c = 0; c < 9; c++) {
                const v = board[r][c];
                if (v === 0) continue;
                if (!map.has(v)) map.set(v, []);
                map.get(v).push(c);
            }
            for (const [v, cols] of map.entries()) {
                if (cols.length > 1) {
                    errors.rows.add(r);
                    cols.forEach(c => conflictSet.add(`${r},${c}`));
                }
            }
        }

        function markDuplicatesInCol(c) {
            const map = new Map(); // value -> [rows...]
            for (let r = 0; r < 9; r++) {
                const v = board[r][c];
                if (v === 0) continue;
                if (!map.has(v)) map.set(v, []);
                map.get(v).push(r);
            }
            for (const [v, rowsArr] of map.entries()) {
                if (rowsArr.length > 1) {
                    errors.cols.add(c);
                    rowsArr.forEach(r => conflictSet.add(`${r},${c}`));
                }
            }
        }

        function markDuplicatesInBox(br, bc) {
            const map = new Map(); // value -> [ [r,c], ... ]
            for (let r = br * 3; r < br * 3 + 3; r++) {
                for (let c = bc * 3; c < bc * 3 + 3; c++) {
                    const v = board[r][c];
                    if (v === 0) continue;
                    if (!map.has(v)) map.set(v, []);
                    map.get(v).push([r, c]);
                }
            }
            const boxIndex = br * 3 + bc;
            for (const [v, cells] of map.entries()) {
                if (cells.length > 1) {
                    errors.boxes.add(boxIndex);
                    cells.forEach(([r, c]) => conflictSet.add(`${r},${c}`));
                }
            }
        }

        // rows
        for (let r = 0; r < 9; r++) {
            markDuplicatesInRow(r);
        }

        // cols
        for (let c = 0; c < 9; c++) {
            markDuplicatesInCol(c);
        }

        // boxes
        for (let br = 0; br < 3; br++) {
            for (let bc = 0; bc < 3; bc++) {
                markDuplicatesInBox(br, bc);
            }
        }

        const valid =
            errors.rows.size === 0 &&
            errors.cols.size === 0 &&
            errors.boxes.size === 0;

        const conflicts = Array.from(conflictSet).map(key => {
            const [r, c] = key.split(",").map(Number);
            return { row: r, col: c };
        });

        return {
            valid,
            rows: Array.from(errors.rows),
            cols: Array.from(errors.cols),
            boxes: Array.from(errors.boxes),
            conflicts,  // 👈 new: exact conflicting cells
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
        
        clearHighlights();
        highlightConflicts(result);

        // 🔔 Check completion: no zeros AND no conflicts
        const empties = countEmptySquares(boardString);
        if (empties === 0 && result.valid) {
            stopTimer();
            console.log("Puzzle completed!");

            const timerEl = document.getElementById("timer");
            const finalTime = timerEl ? timerEl.textContent : "";

            if (window.Swal) {
                Swal.fire({
                    title: "Nice work! 🎉",
                    text: finalTime ? `You finished in ${finalTime}.` : "You solved the puzzle!",
                    icon: "success",
                    confirmButtonText: "New Board"
                }).then(() => {
                    // start a new board with the same difficulty
                    window.BoardUtils.createBoard(currentDifficulty);
                });
            } else {
                // fallback if SweetAlert isn't loaded
                alert("Puzzle completed!");
                window.BoardUtils.createBoard(currentDifficulty);
            }
        }
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

    function createBoard(difficulty = 0.5) {
        const boardEl = document.getElementById('board');
        let puzzle;

        clearChat();

        currentDifficulty = difficulty;

        fetch(`/board/new/${difficulty}`, {
            method: "POST"
        }).then(response => response.json()).then(data => {
            console.log("New board created:", data);
            puzzle = data;
            puzzle_id = data;

        }).then(() => {
            buildGrid(puzzle, boardEl);

            // ⏱ start (or restart) timer on new board
            startTimer();
            
            // Count empties
            const emptyCount = countEmptySquares(puzzle);
            console.log("Empty squares:", emptyCount);
        });
    }


    function clearBoard() {
        const boardEl = document.getElementById("board");
        if (!boardEl) return;

        boardEl.querySelectorAll(".cell").forEach(cell => {
            const isGiven = cell.dataset.given === "true";
            const input = cell.querySelector("input");

            // wipe user-entered values, keep givens
            if (!isGiven && input) {
                input.value = "";
            }

            // remove any visual highlights
            cell.classList.remove("hint", "error");
        });

        // re-check board state (should now be conflict-free, mostly zeros)
        onBoardChanged();
    }

    function clearHighlights() {
        const boardEl = document.getElementById('board');
        boardEl.querySelectorAll('.cell.hint').forEach(cell => {
            cell.classList.remove('hint');
        });
    }

    function highlightCell(row, col) {
        const boardEl = document.getElementById('board');
        if (!boardEl) return;
        
        // clear old
        clearHighlights()
        
        // add to CELL, not input
        const cell = boardEl.querySelector(
            `.cell[data-row="${row}"][data-col="${col}"]`
        );

        if (cell) {
            cell.classList.add('hint');
            const input = cell.querySelector('input');
            if (input) input.focus();
        }
    }

    function highlightConflicts(result) {
        const boardEl = document.getElementById("board");
        if (!boardEl) return;

        // clear old error highlights
        boardEl.querySelectorAll(".cell.error").forEach(cell => {
            cell.classList.remove("error");
        });

        // highlight each conflicting cell
        result.conflicts.forEach(({ row, col }) => {
            const cell = boardEl.querySelector(
                `.cell[data-row="${row}"][data-col="${col}"]`
            );
            if (cell) {
                cell.classList.add("error");
            }
        });
    }

    // --- expose these functions ---
    return {
        validateBoardString,
        onBoardChanged,
        getBoardString,
        buildGrid,
        createBoard,
        highlightCell,
        clearHighlights,
        highlightConflicts,
        clearBoard,
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

    window.BoardUtils.createBoard(strength);
  });
});



window.BoardUtils.createBoard(0.5);