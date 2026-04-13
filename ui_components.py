# ui_components.py
import pygame

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 200, 100)
RED = (200, 50, 50)
YELLOW = (220, 200, 50)
RETRO_BG = (10, 15, 25)

class Button:
    def __init__(self, x, y, width, height, text, font, bg_color=BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, surface):
        color = GREEN if self.is_hovered else self.bg_color
        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        shadow_rect.x += 4
        pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=8)
        
        # Button
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        # Border
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=8)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

def draw_text_with_shadow(surface, text, font, position, color=WHITE, shadow_color=BLACK):
    # Shadow
    text_shadow = font.render(text, True, shadow_color)
    shadow_rect = text_shadow.get_rect(center=(position[0]+3, position[1]+3))
    surface.blit(text_shadow, shadow_rect)
    
    # Text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    surface.blit(text_surface, text_rect)
