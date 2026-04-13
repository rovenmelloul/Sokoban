import copy
from levels import load_level

class SokobanGame:
    def __init__(self, level_index=0):
        self.level_index = level_index
        self.grid = load_level(self.level_index)
        self.history = []
        self.rows = len(self.grid) if self.grid else 0
        self.cols = max((len(r) for r in self.grid)) if self.grid else 0
        self.is_won = False
        self.moves_count = 0
        self.time_elapsed = 0.0

    def reset(self):
        self.grid = load_level(self.level_index)
        self.history = []
        self.is_won = False
        self.moves_count = 0
        self.time_elapsed = 0.0

    def load_level(self, idx):
        self.level_index = idx
        self.reset()
        if self.grid:
            self.rows = len(self.grid)
            self.cols = max(len(r) for r in self.grid)

    def get_player_pos(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] in (3, 5):
                    return r, c
        return None

    def can_move(self, r, c, dr, dc):
        nr, nc = r + dr, c + dc
        
        if nr < 0 or nr >= self.rows or nc < 0 or nc >= self.cols:
            return False
        
        # -1 represents a wall, 0 is empty, 1 is goal, 2 is box, 3 is player, 4 is box on goal, 5 is player on goal
        if self.grid[nr][nc] == -1: 
            return False
            
        if self.grid[nr][nc] in (2, 4):
            nnr, nnc = nr + dr, nc + dc
            if nnr < 0 or nnr >= self.rows or nnc < 0 or nnc >= self.cols:
                return False
            if self.grid[nnr][nnc] in (-1, 2, 4): 
                return False
                
        return True

    def move(self, dr, dc):
        if self.is_won:
            return False

        pos = self.get_player_pos()
        if not pos:
            return False
        
        r, c = pos
        if not self.can_move(r, c, dr, dc):
            return False

        self.history.append(copy.deepcopy(self.grid))
        self.moves_count += 1
        
        nr, nc = r + dr, c + dc
        
        # Si on pousse une caisse
        if self.grid[nr][nc] in (2, 4):
            nnr, nnc = nr + dr, nc + dc
            
            # Remove box
            if self.grid[nr][nc] == 4:
                self.grid[nr][nc] = 1 # Devient cible
            else:
                self.grid[nr][nc] = 0 # Devient vide
                
            # Place un box
            if self.grid[nnr][nnc] == 1:
                self.grid[nnr][nnc] = 4
            else:
                self.grid[nnr][nnc] = 2

        # Move player
        if self.grid[r][c] == 5:
            self.grid[r][c] = 1
        else:
            self.grid[r][c] = 0
            
        if self.grid[nr][nc] == 1:
            self.grid[nr][nc] = 5
        elif self.grid[nr][nc] == 0:
            self.grid[nr][nc] = 3

        self.check_win()
        return True

    def undo(self):
        if self.history:
            self.grid = self.history.pop()
            self.moves_count = max(0, self.moves_count - 1)
            self.is_won = False
            return True
        return False

    def check_win(self):
        # S'il y a des '2' (caisse qui n'est pas sur une cible), alors c'est pas gagné
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 2:
                    self.is_won = False
                    return
        self.is_won = True
