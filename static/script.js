// script.js — Skyscrapers Game Logic
console.log('✅ script.js loaded');

const API_URL = window.location.origin;
console.log('API_URL:', API_URL);

// ===== State =====
let currentClues = null;
let currentSolution = null;
let currentBoard = [];
let gridSize = 4;
let selectedCell = null;
let fixedCells = new Set();
let mistakes = 0;
let seconds = 0;
let timerInterval = null;

// ===== Init =====
window.addEventListener('DOMContentLoaded', () => {
    console.log('✅ DOM loaded, attaching listeners');
    attachEventListeners();
    newGame();
});

function attachEventListeners() {
    // Button click handlers
    const buttons = {
        'homeBtn': () => window.location.href = '/',
        'hintBtn': getHint,
        'solveBtn': () => solveBoard(false),
        'solveAC3Btn': () => solveBoard(true),
        'validateBtn': validateBoard
    };

    for (const [id, fn] of Object.entries(buttons)) {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('click', fn);
            console.log(`✅ Attached listener to #${id}`);
        } else {
            console.error(`❌ Button #${id} not found!`);
        }
    }

        // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (!selectedCell) return;

        if (e.key >= '1' && e.key <= '9') {
            const num = parseInt(e.key);
            if (num <= gridSize) placeNumber(selectedCell.row, selectedCell.col, num);
        }
        else if (e.key === 'Backspace' || e.key === 'Delete') {
            placeNumber(selectedCell.row, selectedCell.col, 0);
        }
        else if (e.key === 'ArrowUp') {
            e.preventDefault();
            moveSelection(-1, 0);
        }
        else if (e.key === 'ArrowDown') {
            e.preventDefault();
            moveSelection(1, 0);
        }
        else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            moveSelection(0, -1);
        }
        else if (e.key === 'ArrowRight') {
            e.preventDefault();
            moveSelection(0, 1);
        }
    });

    // Win modal "Back to Home" button
    const winNewGameBtn = document.getElementById('winNewGame');
    if (winNewGameBtn) {
        winNewGameBtn.addEventListener('click', () => {
            window.location.href = '/';
        });
    }
}

// ===== New Game =====
async function newGame() {
    console.log('🎮 New Game started');
    showMessage('Generating puzzle...');
    resetTimer();
    mistakes = 0;
    document.getElementById('mistakes').textContent = '0';
    document.getElementById('algoUsed').textContent = '—';
    document.getElementById('nodesExplored').textContent = '—';

    // Read grid size and difficulty from URL params (set by landing page)
    const urlParams = new URLSearchParams(window.location.search);
    gridSize = parseInt(urlParams.get('n')) || 4;
    const difficulty = urlParams.get('difficulty') || 'medium';
    console.log(`  Grid: ${gridSize}x${gridSize}, Difficulty: ${difficulty}`);

    try {
        const url = `${API_URL}/generate?n=${gridSize}&difficulty=${difficulty}`;
        console.log('  Fetching:', url);
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const data = await res.json();
        console.log('  Received puzzle');

        currentClues = data.clues;
        currentSolution = data.solution;
        currentBoard = Array.from({ length: gridSize }, () => Array(gridSize).fill(0));
        fixedCells.clear();
        selectedCell = null;
        renderBoard();
        startTimer();
        showMessage(`Puzzle generated in ${data.generation_time_seconds}s. Good luck!`);
    } catch (err) {
        console.error('❌ Error in newGame:', err);
        showMessage('Error: ' + err.message + '. Is the server running?', 'error');
    }
}

// ===== Render =====
function renderBoard() {
    console.log('🎨 Rendering board');
    const container = document.getElementById('boardContainer');
    if (!container) {
        console.error('❌ boardContainer not found');
        return;
    }
    container.innerHTML = '';
    const n = gridSize;
    const totalCols = n + 2;
    const totalRows = n + 2;

    container.style.gridTemplateColumns = `repeat(${totalCols}, auto)`;
    container.style.gridTemplateRows = `repeat(${totalRows}, auto)`;

    // Top-left corner
    const c1 = document.createElement('div');
    c1.className = 'clue corner';
    container.appendChild(c1);

    // Top clues
    for (let c = 0; c < n; c++) {
        const clue = document.createElement('div');
        const val = currentClues.top[c];
        clue.className = 'clue' + (val === 0 ? ' empty' : '');
        clue.textContent = val === 0 ? '·' : val;
        container.appendChild(clue);
    }

    const c2 = document.createElement('div');
    c2.className = 'clue corner';
    container.appendChild(c2);

    // Rows
    for (let r = 0; r < n; r++) {
        const leftClue = document.createElement('div');
        const lv = currentClues.left[r];
        leftClue.className = 'clue' + (lv === 0 ? ' empty' : '');
        leftClue.textContent = lv === 0 ? '·' : lv;
        container.appendChild(leftClue);

        for (let c = 0; c < n; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.addEventListener('click', () => selectCell(r, c));
            container.appendChild(cell);
        }

        const rightClue = document.createElement('div');
        const rv = currentClues.right[r];
        rightClue.className = 'clue' + (rv === 0 ? ' empty' : '');
        rightClue.textContent = rv === 0 ? '·' : rv;
        container.appendChild(rightClue);
    }

    const c3 = document.createElement('div');
    c3.className = 'clue corner';
    container.appendChild(c3);

    for (let c = 0; c < n; c++) {
        const clue = document.createElement('div');
        const val = currentClues.bottom[c];
        clue.className = 'clue' + (val === 0 ? ' empty' : '');
        clue.textContent = val === 0 ? '·' : val;
        container.appendChild(clue);
    }

    const c4 = document.createElement('div');
    c4.className = 'clue corner';
    container.appendChild(c4);

    renderCells();
    renderNumberPad();
    renderLegend();
}

function renderCells() {
    document.querySelectorAll('.cell').forEach(cell => {
        const r = parseInt(cell.dataset.row);
        const c = parseInt(cell.dataset.col);
        const val = currentBoard[r][c];
        cell.innerHTML = '';
        if (val > 0) {
            const building = document.createElement('div');
            building.style.cssText = 'display:flex; flex-direction:column-reverse; align-items:center; width:100%; height:100%; justify-content:flex-start; padding-top:4px;';
            for (let i = 0; i < val; i++) {
                const seg = document.createElement('div');
                seg.className = `segment h${val}`;
                building.appendChild(seg);
            }
            cell.appendChild(building);

            const num = document.createElement('span');
            num.className = 'cell-number';
            num.textContent = val;
            cell.appendChild(num);
        }
        cell.classList.remove('selected', 'hint', 'error', 'solved');
    });
}

function renderLegend() {
    const legend = document.getElementById('legend');
    if (!legend) return;
    legend.innerHTML = '';
    const colors = ['#22c55e', '#3b82f6', '#8b5cf6', '#f43f5e', '#f59e0b', '#d946ef'];
    for (let i = 0; i < gridSize; i++) {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `<span class="swatch" style="background: ${colors[i]}"></span> Height ${i + 1}`;
        legend.appendChild(item);
    }
}

function renderNumberPad() {
    const pad = document.getElementById('numberPad');
    if (!pad) return;
    pad.innerHTML = '';
    for (let i = 1; i <= gridSize; i++) {
        const btn = document.createElement('button');
        btn.className = 'num-btn';
        btn.textContent = i;
        btn.addEventListener('click', () => {
            if (selectedCell) placeNumber(selectedCell.row, selectedCell.col, i);
        });
        pad.appendChild(btn);
    }
    const erase = document.createElement('button');
    erase.className = 'num-btn erase';
    erase.textContent = '⌫';
    erase.addEventListener('click', () => {
        if (selectedCell) placeNumber(selectedCell.row, selectedCell.col, 0);
    });
    pad.appendChild(erase);
}

// ===== Interactions =====
function selectCell(r, c) {
    if (fixedCells.has(`${r},${c}`)) return;
    document.querySelectorAll('.cell').forEach(cell => cell.classList.remove('selected'));
    selectedCell = { row: r, col: c };
    const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
    if (cell) cell.classList.add('selected');
}
function moveSelection(dr, dc) {
    if (!selectedCell) return;
    const newR = selectedCell.row + dr;
    const newC = selectedCell.col + dc;
    if (newR < 0 || newR >= gridSize || newC < 0 || newC >= gridSize) return;
    document.querySelectorAll('.cell').forEach(cell => cell.classList.remove('selected'));
    selectedCell = { row: newR, col: newC };
    const cell = document.querySelector(`.cell[data-row="${newR}"][data-col="${newC}"]`);
    if (cell) cell.classList.add('selected');
}
function placeNumber(r, c, num) {
    if (fixedCells.has(`${r},${c}`)) return;
    currentBoard[r][c] = num;
    renderCells();
    const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
    if (cell) cell.classList.add('selected');

    // Check for constraint violations (duplicates in row/column)
    const hasDuplicate = checkDuplicates(r, c, num);

    if (num !== 0 && hasDuplicate) {
        if (cell) cell.classList.add('error');
        mistakes++;
        document.getElementById('mistakes').textContent = mistakes;
    } else if (num !== 0) {
        if (isBoardComplete()) {
            validateBoard(true);  // Auto-check when board is filled
        }
    }
}

function checkDuplicates(r, c, num) {
    if (num === 0) return false;
    // Check row
    for (let i = 0; i < gridSize; i++) {
        if (i !== c && currentBoard[r][i] === num) return true;
    }
    // Check column
    for (let i = 0; i < gridSize; i++) {
        if (i !== r && currentBoard[i][c] === num) return true;
    }
    return false;
}

function isBoardComplete() {
    for (let r = 0; r < gridSize; r++) {
        for (let c = 0; c < gridSize; c++) {
            if (currentBoard[r][c] === 0) return false;
        }
    }
    return true;
}

// ===== Hints =====
function getHint() {
    console.log('💡 Hint clicked');

    // Check if the board has any wrong entries first
    const hasWrong = currentBoard.some((row, r) =>
        row.some((val, c) => val !== 0 && currentSolution && currentSolution[r][c] !== val)
    );
    if (hasWrong) {
        showMessage('❌ Fix the red cells before asking for a hint.', 'error');
        return;
    }

    // Find the first empty cell and reveal its answer
    for (let r = 0; r < gridSize; r++) {
        for (let c = 0; c < gridSize; c++) {
            if (currentBoard[r][c] === 0) {
                const value = currentSolution[r][c];
                currentBoard[r][c] = value;
                renderCells();
                const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
                if (cell) cell.classList.add('hint');
                showMessage(`💡 Try ${value} at row ${r + 1}, column ${c + 1}`, 'success');
                return;
            }
        }
    }
    showMessage('✅ Board is already complete!', 'success');
}

// ===== Solve =====
async function solveBoard(useAC3) {
    console.log(`🤖 Solve clicked, AC-3: ${useAC3}`);
    showMessage(useAC3 ? 'Solving with AC-3...' : 'Solving with Backtracking + FC + MRV...');
    const endpoint = useAC3 ? '/solve-ac3' : '/solve';
    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: currentBoard, clues: currentClues })
        });
        const data = await res.json();
        if (!data.solved) {
            showMessage('No solution exists.', 'error');
            return;
        }
        currentBoard = data.solution;
        renderCells();
        for (let r = 0; r < gridSize; r++) {
            for (let c = 0; c < gridSize; c++) {
                if (!fixedCells.has(`${r},${c}`)) {
                    const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
                    if (cell) cell.classList.add('solved');
                }
            }
        }
        stopTimer();
        const stats = data.algorithm_stats;
        document.getElementById('algoUsed').textContent = useAC3 ? 'AC-3 + BT' : 'BT + FC + MRV';
        document.getElementById('nodesExplored').textContent = stats.nodes_explored;
        showMessage(`Solved in ${stats.time_seconds}s | Nodes: ${stats.nodes_explored} | Backtracks: ${stats.backtracks}`, 'success');
    } catch (err) {
        console.error('❌ Solve error:', err);
        showMessage('Error solving board.', 'error');
    }
}

// ===== Validate =====
async function validateBoard(autoTriggered = false) {
    console.log('✓ Validate clicked');
    if (!autoTriggered) showMessage('Validating...');
    try {
        const res = await fetch(`${API_URL}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: currentBoard, clues: currentClues })
        });
        const data = await res.json();
        console.log('  Validate response:', data);

        if (data.solved) {
            stopTimer();
            showMessage('🎉 Perfect! The puzzle is correctly solved!', 'success');
            showWinPopup();
        } else if (data.completed && !data.valid) {
            showMessage('❌ Board is complete but has duplicate conflicts.', 'error');
        } else if (data.completed && data.valid && !data.solved) {
            showMessage('⚠️ Board is complete but the edge clues are not satisfied. Recheck your solution.', 'error');
        } else if (data.valid) {
            showMessage('✓ No conflicts so far. Keep going!');
        } else {
            showMessage(`❌ Conflicts at ${data.conflicts.length} cell(s). Fix the red cells.`, 'error');
            data.conflicts.forEach(([r, c]) => {
                const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
                if (cell) cell.classList.add('error');
            });
        }
    } catch (err) {
        console.error('❌ Validate error:', err);
        showMessage('Error validating.', 'error');
    }
}

// ===== Timer =====
function startTimer() {
    stopTimer();
    seconds = 0;
    document.getElementById('timer').textContent = '00:00';
    timerInterval = setInterval(() => {
        seconds++;
        document.getElementById('timer').textContent = formatTime(seconds);
    }, 1000);
}
function stopTimer() { if (timerInterval) clearInterval(timerInterval); timerInterval = null; }
function resetTimer() { stopTimer(); seconds = 0; document.getElementById('timer').textContent = '00:00'; }
function formatTime(s) {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
}

// ===== Win Popup =====
function showWinPopup() {
    document.getElementById('winTime').textContent = formatTime(seconds);
    document.getElementById('winMistakes').textContent = mistakes;
    document.getElementById('winGrid').textContent = `${gridSize}×${gridSize}`;
    setTimeout(() => {
        document.getElementById('winModal').classList.add('visible');
    }, 400);
}

// ===== Message =====
function showMessage(msg, type = '') {
    const el = document.getElementById('message');
    el.textContent = msg;
    el.className = 'message' + (type ? ' ' + type : '');
}
