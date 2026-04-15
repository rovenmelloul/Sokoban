import time
import csv
import heapq
from collections import deque
from levels import LEVELS, load_level
import ai_solver

def run_benchmark():
    results = []
    
    # We will test all available levels
    for lvl_idx in range(len(LEVELS)):
        grid = load_level(lvl_idx)
        print(f"Benchmarking Level {lvl_idx+1}...")
        
        for algo in ['BFS', 'DFS', 'A*']:
            print(f"  -> {algo}...")
            start_time = time.time()
            path = None
            iterations = 0
            
            # Custom implementations to capture iterations
            if algo == 'BFS':
                queue = deque([(grid, [])])
                visited = set()
                visited.add(ai_solver.get_state(grid))
                while queue:
                    iterations += 1
                    if time.time() - start_time > 2.0:
                        path = None
                        break
                    curr, p = queue.popleft()
                    if ai_solver.check_win(curr):
                        path = p
                        break
                    for dr, dc in ai_solver.get_possible_moves(curr):
                        new_grid = ai_solver.apply_move(curr, dr, dc)
                        s = ai_solver.get_state(new_grid)
                        if s not in visited:
                            visited.add(s)
                            queue.append((new_grid, p + [(dr, dc)]))
                            
            elif algo == 'DFS':
                stack = [(grid, [])]
                visited = set()
                visited.add(ai_solver.get_state(grid))
                while stack:
                    iterations += 1
                    if time.time() - start_time > 2.0:
                        path = None
                        break
                    curr, p = stack.pop()
                    if len(p) > 100: continue
                    if ai_solver.check_win(curr):
                        path = p
                        break
                    for dr, dc in ai_solver.get_possible_moves(curr):
                        new_grid = ai_solver.apply_move(curr, dr, dc)
                        s = ai_solver.get_state(new_grid)
                        if s not in visited:
                            visited.add(s)
                            stack.append((new_grid, p + [(dr, dc)]))
                            
            elif algo == 'A*':
                count = 0
                pq = []
                heapq.heappush(pq, (0, count, grid, []))
                visited = set()
                visited.add(ai_solver.get_state(grid))
                while pq:
                    iterations += 1
                    if time.time() - start_time > 2.0:
                        path = None
                        break
                    _, _, curr, p = heapq.heappop(pq)
                    if ai_solver.check_win(curr):
                        path = p
                        break
                    for dr, dc in ai_solver.get_possible_moves(curr):
                        new_grid = ai_solver.apply_move(curr, dr, dc)
                        s = ai_solver.get_state(new_grid)
                        if s not in visited:
                            visited.add(s)
                            count += 1
                            h = ai_solver.heuristic(new_grid)
                            heapq.heappush(pq, (len(p)+1 + h, count, new_grid, p + [(dr, dc)]))
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            status = 'Success' if path else 'Timeout/Failed'
            path_len = len(path) if path else -1
            
            results.append({
                'Level': lvl_idx + 1,
                'Algorithm': algo,
                'Time_Seconds': round(elapsed, 4),
                'Iterations': iterations,
                'Path_Length': path_len,
                'Status': status
            })
            
    with open('results_ia.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Level', 'Algorithm', 'Time_Seconds', 'Iterations', 'Path_Length', 'Status'])
        writer.writeheader()
        writer.writerows(results)
    
    print("Benchmark complete. Data written to results_ia.csv")

if __name__ == '__main__':
    run_benchmark()
