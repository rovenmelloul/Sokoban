import heapq
from collections import deque
import time

try:
    import pygame
except ImportError:
    pygame = None

def get_state(grid):
    pr, pc = -1, -1
    boxes = []
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] in (3, 5):
                pr, pc = r, c
            if grid[r][c] in (2, 4):
                boxes.append((r, c))
    return (pr, pc), frozenset(boxes)

def check_win(grid):
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == 2:
                return False
    return True

def get_possible_moves(grid):
    pr, pc = -1, -1
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] in (3, 5):
                pr, pc = r, c
                break
    moves = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = pr + dr, pc + dc
        if grid[nr][nc] == -1:
            continue
        if grid[nr][nc] in (2, 4):
            nnr, nnc = nr + dr, nc + dc
            if grid[nnr][nnc] in (-1, 2, 4):
                continue
        moves.append((dr, dc))
    return moves

def apply_move(grid, dr, dc):
    new_grid = [row[:] for row in grid]
    pr, pc = -1, -1
    for r in range(len(new_grid)):
        for c in range(len(new_grid[r])):
            if new_grid[r][c] in (3, 5):
                pr, pc = r, c
                
    nr, nc = pr + dr, pc + dc
    if new_grid[nr][nc] in (2, 4):
        nnr, nnc = nr + dr, nc + dc
        new_grid[nr][nc] = 1 if new_grid[nr][nc] == 4 else 0
        new_grid[nnr][nnc] = 4 if new_grid[nnr][nnc] == 1 else 2
        
    new_grid[pr][pc] = 1 if new_grid[pr][pc] == 5 else 0
    
    if new_grid[nr][nc] == 1:
        new_grid[nr][nc] = 5
    elif new_grid[nr][nc] == 0:
        new_grid[nr][nc] = 3
        
    return new_grid

def solve_bfs(initial_grid):
    queue = deque([(initial_grid, [])])
    visited = set()
    initial_state = get_state(initial_grid)
    visited.add(initial_state)
    
    start_time = time.time()
    iterations = 0
    
    while queue:
        iterations += 1
        if iterations % 1000 == 0:
            if pygame: pygame.event.pump()
            if time.time() - start_time > 10.0:
                print("BFS Timeout!")
                return None
        
        grid, path = queue.popleft()
        if check_win(grid):
            return path
        for dr, dc in get_possible_moves(grid):
            new_grid = apply_move(grid, dr, dc)
            state = get_state(new_grid)
            if state not in visited:
                visited.add(state)
                queue.append((new_grid, path + [(dr, dc)]))
    return None

def solve_dfs(initial_grid):
    stack = [(initial_grid, [])]
    visited = set()
    initial_state = get_state(initial_grid)
    visited.add(initial_state)
    
    start_time = time.time()
    iterations = 0
    
    while stack:
        iterations += 1
        if iterations % 1000 == 0:
            if pygame: pygame.event.pump()
            if time.time() - start_time > 10.0:
                print("DFS Timeout!")
                return None
                
        grid, path = stack.pop()
        # limit DFS depth slightly to avoid gigantic paths
        if len(path) > 300:
            continue
            
        if check_win(grid):
            return path
        for dr, dc in get_possible_moves(grid):
            new_grid = apply_move(grid, dr, dc)
            state = get_state(new_grid)
            if state not in visited:
                visited.add(state)
                stack.append((new_grid, path + [(dr, dc)]))
    return None

def heuristic(grid):
    boxes = []
    goals = []
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] in (2, 4):
                boxes.append((r, c))
            if grid[r][c] in (1, 4, 5):
                goals.append((r, c))
    total_dist = 0
    for br, bc in boxes:
        min_d = float('inf')
        for gr, gc in goals:
            d = abs(br - gr) + abs(bc - gc)
            if d < min_d:
                min_d = d
        total_dist += min_d
    return total_dist

def solve_astar(initial_grid):
    count = 0
    pq = []
    heapq.heappush(pq, (0, count, initial_grid, []))
    visited = set()
    initial_state = get_state(initial_grid)
    visited.add(initial_state)
    
    start_time = time.time()
    iterations = 0
    
    while pq:
        iterations += 1
        if iterations % 1000 == 0:
            if pygame: pygame.event.pump()
            if time.time() - start_time > 15.0:
                print("A* Timeout!")
                return None
                
        f_score, _, grid, path = heapq.heappop(pq)
        if check_win(grid):
            return path
        for dr, dc in get_possible_moves(grid):
            new_grid = apply_move(grid, dr, dc)
            state = get_state(new_grid)
            if state not in visited:
                visited.add(state)
                count += 1
                g_score = len(path) + 1
                h_score = heuristic(new_grid)
                heapq.heappush(pq, (g_score + h_score, count, new_grid, path + [(dr, dc)]))
    return None
