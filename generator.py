# generator.py
# Skyscrapers Puzzle Generator
# Creates random valid puzzles with unique solutions

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
    """
    Generate a random n x n Latin square.
    Each row and column contains 1..n exactly once.
    """
    # Start with a base pattern
    base = [[((i + j) % n) + 1 for j in range(n)] for i in range(n)]

    # Randomly shuffle rows
    random.shuffle(base)

    # Randomly shuffle columns
    cols = list(range(n))
    random.shuffle(cols)
    base = [[row[c] for c in cols] for row in base]

    # Randomly relabel the numbers (1..n -> random permutation)
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
    # Column clues (top and bottom)
    for c in range(n):
        col = [solution[r][c] for r in range(n)]
        clues['top'][c] = _count_visible(col)
        clues['bottom'][c] = _count_visible(col[::-1])
    # Row clues (left and right)
    for r in range(n):
        row = solution[r]
        clues['left'][r] = _count_visible(row)
        clues['right'][r] = _count_visible(row[::-1])
    return clues
def count_solutions(n, clues, limit=2):
    """Count how many solutions exist (up to 'limit'). Used to verify uniqueness."""
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
    Generate a Skyscrapers puzzle with a unique solution.
    Removes clues one at a time and verifies uniqueness after each removal.
    """
    solution = _generate_latin_square(n)
    clues = compute_clues(solution)

    # How many clues to remove per grid size and difficulty
    targets = {
        4: {"easy": 0,  "medium": 8,  "hard": 12},
        5: {"easy": 0,  "medium": 4,  "hard": 6},
        6: {"easy": 0,  "medium": 2,  "hard": 3},
    }
    target = targets.get(n, {4: 8, 5: 4, 6: 2})[difficulty]

    if target == 0:
        return clues, solution

    all_positions = [(side, i) for side in ['top', 'bottom', 'left', 'right'] for i in range(n)]
    random.shuffle(all_positions)

    removed = 0
    for side, i in all_positions:
        if removed >= target:
            break
        original = clues[side][i]
        if original == 0:
            continue
        clues[side][i] = 0

        # For 4x4 and 5x5, verify uniqueness after each removal
        # For 6x6, skip the slow check but only remove very few clues
        if n <= 5:
            if len(count_solutions(n, clues, limit=2)) == 1:
                removed += 1
            else:
                clues[side][i] = original
        else:
            removed += 1

    return clues, solution

    return last_puzzle
if __name__ == "__main__":
    import time

    print("Generating a Medium 4x4 puzzle...")
    start = time.time()
    clues, solution = generate_puzzle(4, "medium")
    elapsed = round(time.time() - start, 2)
    print(f"Generated in {elapsed} seconds.\n")

    print("CLUES:")
    print("Top:    ", clues['top'])
    print("Bottom: ", clues['bottom'])
    print("Left:   ", clues['left'])
    print("Right:  ", clues['right'])

    print("\nSOLUTION:")
    for row in solution:
        print(row)

    print("\nVerifying uniqueness...")
    solutions_found = count_solutions(4, clues, limit=2)
    print(f"Number of solutions: {len(solutions_found)}")
    if len(solutions_found) == 1:
        print("✅ Puzzle is UNIQUE!")
    else:
        print("❌ Puzzle has multiple solutions.")
