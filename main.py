import pygame
import sys
import os
import glob
import time

from game import SokobanGame
from ui_components import Button, draw_text_with_shadow, WHITE, RED, GREEN, BLUE, YELLOW, DARK_GRAY, RETRO_BG
import ai_solver
import database
from levels import count_levels

# Initialisation
pygame.init()
pygame.font.init()

# Paramètres
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Sokogame - Retro AI Edition")
clock = pygame.time.Clock()

BASE_FONT = pygame.font.SysFont("courier", 24, bold=True)
TITLE_FONT = pygame.font.SysFont("courier", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("courier", 16, bold=True)

# ---- CHARGEMENT DES ASSETS ----
TILE_SIZE = 64
images = {}
assets_dir = os.path.join("assets", "images")

# Fonction helper pour charger les images
def load_sprite(pattern, default_color):
    files = glob.glob(os.path.join(assets_dir, pattern))
    if files:
        try:
            img = pygame.image.load(files[0]).convert_alpha()
            return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Erreur chargement image {files[0]}: {e}")
    # Fallback
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    surf.fill(default_color)
    pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
    return surf

images['wall'] = load_sprite("wall_sprite_*.png", (100, 40, 40))
images['crate'] = load_sprite("crate_sprite_*.png", (150, 100, 40))
images['crate_on_goal'] = load_sprite("crate_sprite_*.png", (200, 150, 50)) # Optionnel : on pourrait teinter
images['floor'] = load_sprite("floor_sprite_*.png", (100, 100, 100))
images['goal'] = load_sprite("target_sprite_*.png", (200, 50, 50))
images['player'] = load_sprite("character_sprite_*.png", (50, 150, 250))

# Teinter la caisse sur cible pour la remarquer
goal_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
goal_surf.fill((0, 255, 0, 100))
images['crate_on_goal'].blit(goal_surf, (0,0))


# GESTION AUDIO (Fallbacks simples s'il n'y a pas de sons)
# pygame.mixer.init()
# music = pygame.mixer.Sound("assets/sounds/music.wav") ...

# ---- ETATS DU JEU ----
STATE_MENU = 0
STATE_LEVELS = 1
STATE_PLAY = 2
STATE_IA = 3
STATE_IA_WAIT = 4
current_state = STATE_MENU

# ---- DONNEES GLOBALES ----
game = None
player_name = "Player1"
start_time = 0
ai_path = []
ai_step_delay = 300 # ms
last_ai_move_time = 0
ai_moves_count = 0
ia_message = ""

MODE_CLASSIQUE = 0
play_mode = MODE_CLASSIQUE

# ---- BOUTONS DU MENU ----
btn_play_classic = Button(WIDTH//2 - 120, 200, 240, 50, "JOUER", BASE_FONT)
btn_quit = Button(WIDTH//2 - 120, 280, 240, 50, "QUITTER", BASE_FONT)

# ---- BOUTONS DE JEU ----
btn_undo = Button(20, HEIGHT - 60, 120, 40, "ANNULER", SMALL_FONT, bg_color=(200, 150, 50))
btn_reset = Button(150, HEIGHT - 60, 120, 40, "REJOUER", SMALL_FONT, bg_color=(200, 50, 50))
btn_menu = Button(280, HEIGHT - 60, 120, 40, "MENU", SMALL_FONT, bg_color=(100, 100, 100))

# Boutons IA (dans le jeu)
btn_bfs = Button(WIDTH - 140, 20, 120, 40, "IA: BFS", SMALL_FONT, bg_color=(50, 100, 150))
btn_dfs = Button(WIDTH - 140, 70, 120, 40, "IA: DFS", SMALL_FONT, bg_color=(50, 150, 100))
btn_astar = Button(WIDTH - 140, 120, 120, 40, "IA: A*", SMALL_FONT, bg_color=(150, 50, 150))

# Boutons menu niveaux
btn_levels = []
for i in range(count_levels()):
    x = 100 + (i % 4) * 150
    y = 150 + (i // 4) * 100
    btn_levels.append((Button(x, y, 100, 50, f"Niv {i+1}", BASE_FONT), i))

# Initialiser la BD
database.init_db()

def draw_grid(surface, grid):
    rows = len(grid)
    cols = max(len(r) for r in grid) if rows > 0 else 0
    
    board_width = cols * TILE_SIZE
    board_height = rows * TILE_SIZE
    
    offset_x = (WIDTH - board_width) // 2
    offset_y = (HEIGHT - 100 - board_height) // 2 # -100 to leave space for UI at bottom

    for r in range(rows):
        for c in range(len(grid[r])):
            val = grid[r][c]
            x = offset_x + c * TILE_SIZE
            y = offset_y + r * TILE_SIZE
            
            # Draw floor behind everything except wall
            if val != -1:
                surface.blit(images['floor'], (x, y))

            if val == -1:
                surface.blit(images['wall'], (x, y))
            elif val == 1:
                surface.blit(images['goal'], (x, y))
            elif val == 2:
                surface.blit(images['crate'], (x, y))
            elif val == 3:
                surface.blit(images['player'], (x, y))
            elif val == 4:
                surface.blit(images['goal'], (x, y))
                surface.blit(images['crate_on_goal'], (x, y))
            elif val == 5:
                surface.blit(images['goal'], (x, y))
                surface.blit(images['player'], (x, y))

def draw_hud(surface, game_ref, time_elapsed):
    pygame.draw.rect(surface, DARK_GRAY, (0, HEIGHT - 80, WIDTH, 80))
    # Draw scores/moves
    moves_txt = f"Coups: {game_ref.moves_count}"
    time_txt = f"Temps: {int(time_elapsed)}s"
    level_txt = f"Niveau: {game_ref.level_index + 1}"
    
    draw_text_with_shadow(surface, moves_txt, SMALL_FONT, (WIDTH - 150, HEIGHT - 50))
    draw_text_with_shadow(surface, time_txt, SMALL_FONT, (WIDTH - 150, HEIGHT - 20))
    draw_text_with_shadow(surface, level_txt, SMALL_FONT, (WIDTH - 300, HEIGHT - 35))

    btn_undo.draw(surface)
    btn_reset.draw(surface)
    btn_menu.draw(surface)
    
    btn_bfs.draw(surface)
    btn_dfs.draw(surface)
    btn_astar.draw(surface)

def run_ai(algo_name):
    global current_state, ai_path, last_ai_move_time, ai_moves_count, ia_message
    print(f"Lancement {algo_name}...")
    if algo_name == "BFS":
        path = ai_solver.solve_bfs(game.grid)
    elif algo_name == "DFS":
        path = ai_solver.solve_dfs(game.grid)
    else:
        path = ai_solver.solve_astar(game.grid)
        
    if path:
        print(f"Solution trouvée en {len(path)} coups.")
        ai_path = path
        ai_moves_count = len(path)
        ia_message = f"SOLUTION TROUVEE : {ai_moves_count} COUPS ! (Espace pour voir)"
        current_state = STATE_IA_WAIT
        last_ai_move_time = pygame.time.get_ticks()
    else:
        ia_message = "AUCUNE SOLUTION TROUVEE (Espace pour fermer)"
        current_state = STATE_IA_WAIT
        print("Aucune solution trouvée ou Timeout !")

running = True
while running:
    surface = screen
    surface.fill(RETRO_BG)
    
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
    if current_state == STATE_MENU:
        draw_text_with_shadow(surface, "MY SOKOGAME", TITLE_FONT, (WIDTH//2, 100), YELLOW)
        btn_play_classic.draw(surface)
        btn_quit.draw(surface)
        
        for event in events:
            if btn_play_classic.update(event):
                current_state = STATE_LEVELS
            if btn_quit.update(event):
                running = False
                
    elif current_state == STATE_LEVELS:
        draw_text_with_shadow(surface, "CHOIX DU NIVEAU", TITLE_FONT, (WIDTH//2, 50), YELLOW)
        
        for btn, idx in btn_levels:
            btn.bg_color = BLUE
            btn.draw(surface)
            
        btn_menu.draw(surface)
            
        for event in events:
            if btn_menu.update(event):
                current_state = STATE_MENU
                
            for btn, lvl_idx in btn_levels:
                if btn.update(event):
                    play_mode = MODE_CLASSIQUE
                    game = SokobanGame(lvl_idx)
                    start_time = time.time()
                    current_state = STATE_PLAY

    elif current_state == STATE_PLAY:
        time_elapsed = time.time() - start_time
        
        # Check Win
        if game.is_won:
            draw_grid(surface, game.grid)
            draw_hud(surface, game, time_elapsed)
            draw_text_with_shadow(surface, "VICTOIRE !", TITLE_FONT, (WIDTH//2, HEIGHT//2), GREEN)
            pygame.display.flip()
            # Save score
            database.save_score(game.level_index, player_name, game.moves_count, int(time_elapsed))
            pygame.time.wait(2000)
            current_state = STATE_LEVELS
            continue

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.move(-1, 0)
                elif event.key == pygame.K_DOWN:
                    game.move(1, 0)
                elif event.key == pygame.K_LEFT:
                    game.move(0, -1)
                elif event.key == pygame.K_RIGHT:
                    game.move(0, 1)
                elif event.key == pygame.K_z: # Undo (Z on azerty)
                    game.undo()
                elif event.key == pygame.K_r: # Reset
                    game.reset()
                    start_time = time.time()
                elif event.key == pygame.K_ESCAPE:
                    current_state = STATE_LEVELS

            if btn_undo.update(event):
                game.undo()
            if btn_reset.update(event):
                game.reset()
                start_time = time.time()
            if btn_menu.update(event):
                current_state = STATE_LEVELS
                
            if btn_bfs.update(event):
                game.reset() # Start IA from scratch
                run_ai("BFS")
            if btn_dfs.update(event):
                game.reset()
                run_ai("DFS")
            if btn_astar.update(event):
                game.reset()
                run_ai("A*")

        draw_grid(surface, game.grid)
        draw_hud(surface, game, time_elapsed)

    elif current_state == STATE_IA_WAIT:
        draw_grid(surface, game.grid)
        draw_text_with_shadow(surface, ia_message, BASE_FONT, (WIDTH//2, HEIGHT - 50), YELLOW)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if ai_path:
                    current_state = STATE_IA
                    last_ai_move_time = pygame.time.get_ticks()
                else:
                    game.reset()
                    current_state = STATE_PLAY

    elif current_state == STATE_IA:
        # Affichage du replay IA
        draw_grid(surface, game.grid)
        
        draw_text_with_shadow(surface, f"REPLAY IA ({len(ai_path)} Restants)", BASE_FONT, (WIDTH//2, 40), YELLOW)
        
        btn_menu.draw(surface)
        for event in events:
            if btn_menu.update(event):
                current_state = STATE_LEVELS
                
        now = pygame.time.get_ticks()
        if now - last_ai_move_time > ai_step_delay:
            if ai_path:
                dr, dc = ai_path.pop(0)
                game.move(dr, dc)
                last_ai_move_time = now
            else:
                pygame.time.wait(1000) # Finish replay
                current_state = STATE_LEVELS

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
