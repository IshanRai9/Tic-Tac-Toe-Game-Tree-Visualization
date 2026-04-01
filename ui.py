import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, bg_color=(200, 200, 200), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, surface):
        # Slightly lighter color on hover
        color = (min(255, self.bg_color[0] + 30), min(255, self.bg_color[1] + 30), min(255, self.bg_color[2] + 30)) if self.hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                return True
        return False

class Toggle:
    def __init__(self, x, y, width, height, text1, text2, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text1 = text1
        self.text2 = text2
        self.font = font
        self.state = True # True displays text1, False displays text2
        self.hovered = False
        self.bg_color = (200, 220, 255)
        
    def draw(self, surface):
        color = (220, 240, 255) if self.hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 200), self.rect, 2, border_radius=8)
        
        text = self.text1 if self.state else self.text2
        text_surf = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.state = not self.state
                return True
        return False
