# csp_solver.py
# Skyscrapers CSP Solver
# Algorithms: Backtracking, Forward Checking, MRV, Degree Heuristic, LCV, AC-3

class SkyscrapersCSP:
    def __init__(self, n, clues, initial_board=None):
        """
        n: size of the grid (e.g., 4, 5, or 6)
        clues: dict with keys 'top', 'bottom', 'left', 'right'
               each is a list of length n (0 means no clue for that position)
        initial_board: optional 2D list of fixed cells (0 means empty)
        """
        self.n = n
        self.clues = clues
        self.board = initial_board or [[0] * n for _ in range(n)]
        self.variables = [(r, c) for r in range(n) for c in range(n)]
        self.domains = {}
        self.neighbors = {}
        self.nodes_explored = 0
        self.backtracks = 0
        self._initialize_domains()
        self._initialize_neighbors()
        self._apply_clue_pruning()
    def _initialize_domains(self):
        """Set up the initial domain for each cell."""
        for r, c in self.variables:
            if self.board[r][c] != 0:
                self.domains[(r, c)] = {self.board[r][c]}
            else:
                self.domains[(r, c)] = set(range(1, self.n + 1))
    def _initialize_neighbors(self):
        """Precompute which cells share a row or column with each cell."""
        for r, c in self.variables:
            neighbors = set()
            for i in range(self.n):
                if i != c:
                    neighbors.add((r, i))  # Same row
                if i != r:
                    neighbors.add((i, c))  # Same column
            self.neighbors[(r, c)] = neighbors
    def _apply_clue_pruning(self):
        """Use edge clues to shrink domains before solving."""
        n = self.n
        # Row clues (left and right)
        for r in range(n):
            left_clue = self.clues['left'][r]
            right_clue = self.clues['right'][r]
            if left_clue == n:
                for c in range(n):
                    self.domains[(r, c)] = {c + 1}
            if right_clue == n:
                for c in range(n):
                    self.domains[(r, c)] = {n - c}
        # Column clues (top and bottom)
        for c in range(n):
            top_clue = self.clues['top'][c]
            bottom_clue = self.clues['bottom'][c]
            if top_clue == n:
                for r in range(n):
                    self.domains[(r, c)] = {r + 1}
            if bottom_clue == n:
                for r in range(n):
                    self.domains[(r, c)] = {n - r}
    def _count_visible(self, line):
        """Count how many buildings are visible from the start of the line."""
        count = 0
        max_seen = 0
        for h in line:
            if h > max_seen:
                count += 1
                max_seen = h
        return count
    def is_consistent(self, var, value, assignment):
        """Check row, column, and clue constraints."""
        r, c = var
        # Check row/column uniqueness
        for neighbor in self.neighbors[var]:
            if neighbor in assignment and assignment[neighbor] == value:
                return False

        n = self.n
        # Check row clue (only when the row is complete)
        row_complete = all((r, i) in assignment or (r, i) == var for i in range(n))
        if row_complete:
            row = []
            for i in range(n):
                if (r, i) == var:
                    row.append(value)
                else:
                    row.append(assignment[(r, i)])
            if self.clues['left'][r] and self._count_visible(row) != self.clues['left'][r]:
                return False
            if self.clues['right'][r] and self._count_visible(row[::-1]) != self.clues['right'][r]:
                return False

        # Check column clue (only when the column is complete)
        col_complete = all((i, c) in assignment or (i, c) == var for i in range(n))
        if col_complete:
            col = []
            for i in range(n):
                if (i, c) == var:
                    col.append(value)
                else:
                    col.append(assignment[(i, c)])
            if self.clues['top'][c] and self._count_visible(col) != self.clues['top'][c]:
                return False
            if self.clues['bottom'][c] and self._count_visible(col[::-1]) != self.clues['bottom'][c]:
                return False

        return True
    def select_unassigned_variable(self, assignment, domains):
        """MRV (Minimum Remaining Values) + Degree Heuristic."""
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None

        min_size = min(len(domains[v]) for v in unassigned)
        candidates = [v for v in unassigned if len(domains[v]) == min_size]

        if len(candidates) == 1:
            return candidates[0]

        def degree(var):
            return sum(1 for nb in self.neighbors[var] if nb not in assignment)

        return max(candidates, key=degree)
    def order_domain_values(self, var, assignment, domains):
        """LCV (Least Constraining Value) - try values that rule out fewest options first."""
        def count_conflicts(value):
            count = 0
            for nb in self.neighbors[var]:
                if nb not in assignment and value in domains[nb]:
                    count += 1
            return count
        return sorted(domains[var], key=count_conflicts)

    def forward_check(self, var, value, assignment, domains):
        """Remove value from unassigned neighbors. Return None if any domain becomes empty."""
        new_domains = {v: set(domains[v]) for v in domains}
        for nb in self.neighbors[var]:
            if nb not in assignment and value in new_domains[nb]:
                new_domains[nb].remove(value)
                if len(new_domains[nb]) == 0:
                    return None
        return new_domains

    def ac3(self, domains):
        """AC-3 algorithm for arc consistency."""
        queue = []
        for var in self.variables:
            for nb in self.neighbors[var]:
                queue.append((var, nb))
        while queue:
            xi, xj = queue.pop(0)
            if self._revise(domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, domains, xi, xj):
        revised = False
        for value in set(domains[xi]):
            # Check if xj has any value other than 'value'
            if all(value == other for other in domains[xj]):
                domains[xi].remove(value)
                revised = True
        return revised
    def backtracking_search(self, use_forward_checking=True, use_ac3=False):
        """Main backtracking search with optional Forward Checking and AC-3."""
        self.nodes_explored = 0
        self.backtracks = 0
        domains = {v: set(self.domains[v]) for v in self.variables}

        if use_ac3:
            if not self.ac3(domains):
                return None

        assignment = {}
        for r, c in self.variables:
            if self.board[r][c] != 0:
                assignment[(r, c)] = self.board[r][c]

        return self._backtrack(assignment, domains, use_forward_checking)

    def _backtrack(self, assignment, domains, use_fc):
        self.nodes_explored += 1
        if len(assignment) == self.n * self.n:
            # Full validation against ALL clues before accepting
            if self._validate_assignment(assignment):
                return assignment
            # Invalid solution — reject and keep searching
            return None

        var = self.select_unassigned_variable(assignment, domains)
        if var is None:
            return None

        for value in self.order_domain_values(var, assignment, domains):
            if self.is_consistent(var, value, assignment):
                assignment[var] = value
                if use_fc:
                    new_domains = self.forward_check(var, value, assignment, domains)
                    if new_domains is not None:
                        result = self._backtrack(assignment, new_domains, use_fc)
                        if result is not None:
                            return result
                else:
                    result = self._backtrack(assignment, domains, use_fc)
                    if result is not None:
                        return result
                del assignment[var]
                self.backtracks += 1
        return None
    def _validate_assignment(self, assignment):
        """Fully validate a complete assignment against all clue constraints."""
        n = self.n
        # Check all rows
        for r in range(n):
            row = [assignment[(r, c)] for c in range(n)]
            if self.clues['left'][r] and self._count_visible(row) != self.clues['left'][r]:
                return False
            if self.clues['right'][r] and self._count_visible(row[::-1]) != self.clues['right'][r]:
                return False
        # Check all columns
        for c in range(n):
            col = [assignment[(r, c)] for r in range(n)]
            if self.clues['top'][c] and self._count_visible(col) != self.clues['top'][c]:
                return False
            if self.clues['bottom'][c] and self._count_visible(col[::-1]) != self.clues['bottom'][c]:
                return False
        return True
    def solve(self):
        """Public method to solve the puzzle. Returns solved board or None."""
        result = self.backtracking_search()
        if result is None:
            return None
        n = self.n
        board = [[0] * n for _ in range(n)]
        for (r, c), val in result.items():
            board[r][c] = val
        return board

    def get_stats(self):
        """Return algorithm statistics."""
        return {
            "nodes_explored": self.nodes_explored,
            "backtracks": self.backtracks
        }

if __name__ == "__main__":
    clues = {
        'top':    [2, 2, 1, 3],
        'bottom': [3, 1, 2, 2],
        'left':   [3, 1, 2, 2],
        'right':  [2, 2, 1, 3]
    }
    solver = SkyscrapersCSP(4, clues)
    solution = solver.solve()
    if solution:
        for row in solution:
            print(row)
        print("Stats:", solver.get_stats())
    else:
        print("No solution found.")
