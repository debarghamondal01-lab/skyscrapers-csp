# main.py
# FastAPI Backend for Skyscrapers CSP Game

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import time

from csp_solver import SkyscrapersCSP
from generator import generate_puzzle

app = FastAPI(title="Skyscrapers CSP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------- Models ----------
class BoardInput(BaseModel):
    board: List[List[int]]

class SolveInput(BaseModel):
    board: List[List[int]]
    clues: dict

class HintRequest(BaseModel):
    board: List[List[int]]
    clues: dict


# ---------- Helpers ----------
def _count_visible(line):
    count = 0
    max_seen = 0
    for h in line:
        if h > max_seen:
            count += 1
            max_seen = h
    return count


def _solve_with_clues(board, clues, use_ac3=False):
    n = len(board)
    start = time.time()
    solver = SkyscrapersCSP(n, clues, initial_board=board)

    # Auto-apply AC-3 for larger grids to prevent explosion in search space
    auto_ac3 = (n >= 5)
    actual_ac3 = use_ac3 or auto_ac3

    if actual_ac3:
        result = solver.backtracking_search(use_forward_checking=True, use_ac3=True)
        if result is None:
            return {"solved": False, "solution": None}
        sol = [[0] * n for _ in range(n)]
        for (r, c), val in result.items():
            sol[r][c] = val
    else:
        sol = solver.solve()
        if sol is None:
            return {"solved": False, "solution": None}

    elapsed = round(time.time() - start, 4)
    stats = solver.get_stats()
    stats["time_seconds"] = elapsed
    return {"solved": True, "solution": sol, "algorithm_stats": stats}


# ---------- Endpoints ----------
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/generate")
def generate(n: int = 4, difficulty: str = "medium"):
    start = time.time()
    clues, solution = generate_puzzle(n, difficulty)
    elapsed = round(time.time() - start, 3)
    return {
        "n": n,
        "difficulty": difficulty,
        "clues": clues,
        "solution": solution,
        "generation_time_seconds": elapsed
    }

@app.post("/solve")
def solve_endpoint(data: SolveInput):
    return _solve_with_clues(data.board, data.clues, use_ac3=False)

@app.post("/solve-ac3")
def solve_ac3_endpoint(data: SolveInput):
    return _solve_with_clues(data.board, data.clues, use_ac3=True)

@app.post("/hint")
def get_hint(data: HintRequest):
    n = len(data.board)
    solver = SkyscrapersCSP(n, data.clues, initial_board=data.board)
    solution = solver.solve()
    if solution is None:
        return {"hint": None, "message": "No solution exists for this board."}
    for r in range(n):
        for c in range(n):
            if data.board[r][c] == 0:
                return {
                    "row": r,
                    "col": c,
                    "value": solution[r][c],
                    "message": f"Try {solution[r][c]} at row {r+1}, column {c+1}"
                }
    return {"hint": None, "message": "Board is already complete!"}

@app.post("/validate")
def validate(data: SolveInput):
    board = data.board
    clues = data.clues
    n = len(board)

    def has_conflict(r, c):
        val = board[r][c]
        if val == 0:
            return False
        for i in range(n):
            if i != c and board[r][i] == val:
                return True
        for i in range(n):
            if i != r and board[i][c] == val:
                return True
        return False

    conflicts = []
    for r in range(n):
        for c in range(n):
            if has_conflict(r, c):
                conflicts.append([r, c])

    filled = all(board[r][c] != 0 for r in range(n) for c in range(n))

    solved = False
    if filled and len(conflicts) == 0:
        clues_ok = True
        for c in range(n):
            col = [board[r][c] for r in range(n)]
            if clues['top'][c] and _count_visible(col) != clues['top'][c]:
                clues_ok = False
            if clues['bottom'][c] and _count_visible(col[::-1]) != clues['bottom'][c]:
                clues_ok = False
        for r in range(n):
            row = board[r]
            if clues['left'][r] and _count_visible(row) != clues['left'][r]:
                clues_ok = False
            if clues['right'][r] and _count_visible(row[::-1]) != clues['right'][r]:
                clues_ok = False
        solved = clues_ok

    return {
        "valid": len(conflicts) == 0,
        "conflicts": conflicts,
        "completed": filled,
        "solved": solved
    }
