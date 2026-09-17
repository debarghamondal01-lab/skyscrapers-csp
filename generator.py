# generator.py
# Skyscrapers Puzzle Generator

import random
from csp_solver import SkyscrapersCSP


def _count_visible(line):
    """Count buildings visible from the start of a line."""
    count = 0
    max_seen = 0
    for h in line:
        if h > max_seen:
            count += 1
            max_seen = h
    return count


def _generate_latin_square(n):
    """Generate a random n x n Latin square."""
    base = [[((i + j) % n) + 1 for j in range(n)] for i in range(n)]
    random.shuffle(base)
    cols = list(range(n))
    random.shuffle(cols)
    base = [[row[c] for c in cols] for row in base]
    symbols = list(range(1, n + 1))
    random.shuffle(symbols)
    mapping = {i + 1: symbols[i] for i in range(n)}
    base = [[mapping[cell] for cell in row] for row in base]
    return base


def compute_clues(solution):
    """Given a solved grid, calculate all 4 edge clues."""
    n = len(solution)
    clues = {
        'top':    [0] * n,
        'bottom': [0] * n,
        'left':   [0] * n,
        'right':  [0] * n
    }
    for c in range(n):
        col = [solution[r][c] for r in range(n)]
        clues['top'][c] = _count_visible(col)
        clues['bottom'][c] = _count_visible(col[::-1])
    for r in range(n):
        row = solution[r]
        clues['left'][r] = _count_visible(row)
        clues['right'][r] = _count_visible(row[::-1])
    return clues


def count_solutions(n, clues, limit=2):
    """Count how many solutions exist (up to 'limit')."""
    solver = SkyscrapersCSP(n, clues)
    solutions = []
    domains = {v: set(solver.domains[v]) for v in solver.variables}
    assignment = {}

    def backtrack(assignment, domains):
        if len(solutions) >= limit:
            return
        if len(assignment) == n * n:
            sol = [[0] * n for _ in range(n)]
            for (r, c), val in assignment.items():
                sol[r][c] = val
            solutions.append(sol)
            return
        var = solver.select_unassigned_variable(assignment, domains)
        if var is None:
            return
        for value in list(domains[var]):
            if solver.is_consistent(var, value, assignment):
                assignment[var] = value
                new_domains = solver.forward_check(var, value, assignment, domains)
                if new_domains is not None:
                    backtrack(assignment, new_domains)
                del assignment[var]

    backtrack(assignment, domains)
    return solutions


def generate_puzzle(n=4, difficulty="medium"):
    """
    Generate a Skyscrapers puzzle. Guaranteed solvable by construction:
    we start from a valid Latin square and only remove clues from it.
    """
    targets = {
        4: {"easy": 0,  "medium": 8,  "hard": 12},
        5: {"easy": 0,  "medium": 4,  "hard": 6},
        6: {"easy": 0,  "medium": 2,  "hard": 3},
    }
    target = targets.get(n, {4: 8, 5: 4, 6: 2})[difficulty]

    solution = _generate_latin_square(n)
    clues = compute_clues(solution)

    if target > 0:
        all_positions = [(side, i) for side in ['top', 'bottom', 'left', 'right'] for i in range(n)]
        random.shuffle(all_positions)
        removed = 0
        for side, i in all_positions:
            if removed >= target:
                break
            if clues[side][i] == 0:
                continue
            original = clues[side][i]
            clues[side][i] = 0

            # For 4×4 and 5×5, verify uniqueness (fast)
            if n <= 5:
                if len(count_solutions(n, clues, limit=2)) == 1:
                    removed += 1
                else:
                    clues[side][i] = original
            else:
                # For 6×6, skip uniqueness check (fast path)
                removed += 1

    return clues, solution
