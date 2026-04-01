import pygame

class TreeVisualizer:
    def __init__(self, rect):
        self.rect = rect
        self.root = None
        self.camera_y = 0
        self.camera_x = 0
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 14)
        self.hovered_node = None

    def set_tree(self, root):
        self.root = root
        self.camera_x = 0
        # Reset camera Y depending on if we want to start from the top
        self.camera_y = 50 
        if self.root:
            # We want to use the full width of the rect, but maybe standard spacing is better
            # For simplicity, calculate base width off tree structure or fixed rect
            self._calculate_positions(self.root, 0, max(self.rect.width, 2000), 50)
            
            # Center the camera on the root
            self.camera_x = -(self.root.x - self.rect.width // 2)

    def _calculate_positions(self, node, left, right, y):
        width = right - left
        node.x = left + width // 2
        node.y = y
        
        # Calculate for children
        if not node.children:
            return
            
        child_width = width / max(1, len(node.children))
        for i, child in enumerate(node.children):
            c_left = left + i * child_width
            c_right = c_left + child_width
            self._calculate_positions(child, c_left, c_right, y + 80)

    def process_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[0]: # Left click drag for panning
                self.camera_x += event.rel[0]
                self.camera_y += event.rel[1]
                
            mx, my = event.pos
            if self.rect.collidepoint((mx, my)):
                # Adjust for camera
                self.hovered_node = self._get_node_at(self.root, mx - self.rect.x - self.camera_x, my - self.rect.y - self.camera_y)
            else:
                self.hovered_node = None
                
    def _get_node_at(self, node, x, y):
        if not node: return None
        # Check collision with circle of radius 15
        if (node.x - x)**2 + (node.y - y)**2 <= 15**2:
            return node
            
        for child in node.children:
            found = self._get_node_at(child, x, y)
            if found: return found
        return None

    def draw(self, surface):
        # Draw background panel
        pygame.draw.rect(surface, (250, 250, 250), self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)
        
        # Clip specifically to this rect
        original_clip = surface.get_clip()
        surface.set_clip(self.rect)
        
        if self.root:
            self._draw_edges(surface, self.root)
            self._draw_nodes(surface, self.root)
            
        if self.hovered_node and not getattr(self.hovered_node, 'is_pruned', False):
            self._draw_tooltip(surface, self.hovered_node)
            
        # Restore clip
        surface.set_clip(original_clip)
        
    def _draw_edges(self, surface, node):
        for child in node.children:
            color = (180, 180, 180)
            width = 1
            if child.move == node.best_move and not child.is_pruned:
                color = (50, 220, 50) # Highlight optimal path
                width = 3
                
            start_pos = (node.x + self.rect.x + self.camera_x, node.y + self.rect.y + self.camera_y)
            end_pos = (child.x + self.rect.x + self.camera_x, child.y + self.rect.y + self.camera_y)
            
            pygame.draw.line(surface, color, start_pos, end_pos, width)
            self._draw_edges(surface, child)

    def _draw_nodes(self, surface, node):
        x = int(node.x + self.rect.x + self.camera_x)
        y = int(node.y + self.rect.y + self.camera_y)
        
        # Don't draw if heavily out of bounds
        if -50 < x < self.rect.width + 50 and -50 < y < self.rect.height + 50:
            if node.is_pruned:
                pygame.draw.circle(surface, (220, 100, 100), (x, y), 8)
                pygame.draw.circle(surface, (0, 0, 0), (x, y), 8, 1)
            else:
                color = (100, 180, 250) if node.player == -1 else (250, 180, 100) 
                if node.player is None: color = (200, 200, 200) # Root node
                
                pygame.draw.circle(surface, color, (x, y), 16)
                pygame.draw.circle(surface, (0, 0, 0), (x, y), 16, 1)
                
                score_text = self.small_font.render(str(node.score), True, (0, 0, 0))
                score_rect = score_text.get_rect(center=(x, y))
                surface.blit(score_text, score_rect)
            
        for child in node.children:
            self._draw_nodes(surface, child)
            
    def _draw_tooltip(self, surface, node):
        # Draw small board representation near mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tool_rect = pygame.Rect(mouse_x + 15, mouse_y + 15, 90, 90)
        
        # Keep inside visualizer bounds
        if tool_rect.right > self.rect.right: tool_rect.x = mouse_x - 105
        if tool_rect.bottom + 40 > self.rect.bottom: tool_rect.y = mouse_y - 145
        
        # Draw Board Back
        pygame.draw.rect(surface, (255, 255, 240), tool_rect)
        pygame.draw.rect(surface, (0, 0, 0), tool_rect, 1)
        
        b = node.board
        if b is not None:
            # draw grid lines
            for i in range(1, 3):
                pygame.draw.line(surface, (0, 0, 0), (tool_rect.x + i*30, tool_rect.y), (tool_rect.x + i*30, tool_rect.bottom), 1)
                pygame.draw.line(surface, (0, 0, 0), (tool_rect.x, tool_rect.y + i*30), (tool_rect.right, tool_rect.y + i*30), 1)
                
            for r in range(3):
                for c in range(3):
                    center = (tool_rect.x + c*30 + 15, tool_rect.y + r*30 + 15)
                    if b[r][c] == 1:
                        text = self.font.render("X", True, (0, 0, 255))
                        surface.blit(text, text.get_rect(center=center))
                    elif b[r][c] == -1:
                        text = self.font.render("O", True, (255, 0, 0))
                        surface.blit(text, text.get_rect(center=center))
        
        # Draw stats below tooltip
        if node.alpha is not None:
            stats_rect = pygame.Rect(tool_rect.x, tool_rect.bottom, 90, 40)
            pygame.draw.rect(surface, (240, 240, 240), stats_rect)
            pygame.draw.rect(surface, (0, 0, 0), stats_rect, 1)
            
            alpha_str = "inf" if node.alpha == float('inf') else "-inf" if node.alpha == float('-inf') else str(node.alpha)
            beta_str = "inf" if node.beta == float('inf') else "-inf" if node.beta == float('-inf') else str(node.beta)
            
            stat_text = self.small_font.render(f"A:{alpha_str} B:{beta_str}", True, (0, 0, 0))
            surface.blit(stat_text, (stats_rect.x + 4, stats_rect.y + 4))
            stat2 = self.small_font.render(f"Score: {node.score}", True, (0, 0, 0))
            surface.blit(stat2, (stats_rect.x + 4, stats_rect.y + 20))
