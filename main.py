import pygame
import sys
from game import TicTacToe
from ai import get_best_move
from ui import Button, Toggle
from tree_visualizer import TreeVisualizer

pygame.init()

# Setup Screen
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe Game Tree Visualization")

# Colors
BG_COLOR = (240, 240, 240)
LINE_COLOR = (50, 50, 50)

# Fonts
font = pygame.font.SysFont(None, 48)
ui_font = pygame.font.SysFont(None, 24)

# Create objects
game = TicTacToe()
visualizer = TreeVisualizer(pygame.Rect(400, 0, 800, HEIGHT))

# UI Components
algo_toggle = Toggle(50, 50, 250, 40, "Algorithm: Minimax", "Algorithm: Alpha-Beta", ui_font)
mode_toggle = Toggle(50, 100, 250, 40, "Mode: Human vs AI", "Mode: AI vs AI", ui_font)
restart_btn = Button(50, 150, 250, 40, "Restart Game", ui_font)

board_rect = pygame.Rect(50, 300, 300, 300)

def draw_board(surface):
    # Draw Left panel background
    pygame.draw.rect(surface, BG_COLOR, (0, 0, 400, HEIGHT))
    pygame.draw.line(surface, (100, 100, 100), (400, 0), (400, HEIGHT), 2)
    
    # Draw grid
    for i in range(1, 3):
        pygame.draw.line(surface, LINE_COLOR, (board_rect.x + i * 100, board_rect.y), (board_rect.x + i * 100, board_rect.bottom), 5)
        pygame.draw.line(surface, LINE_COLOR, (board_rect.x, board_rect.y + i * 100), (board_rect.right, board_rect.y + i * 100), 5)
        
    for r in range(3):
        for c in range(3):
            if game.board[r][c] == 1:
                text = font.render("X", True, (0, 0, 255))
                rect = text.get_rect(center=(board_rect.x + c * 100 + 50, board_rect.y + r * 100 + 50))
                surface.blit(text, rect)
            elif game.board[r][c] == -1:
                text = font.render("O", True, (255, 0, 0))
                rect = text.get_rect(center=(board_rect.x + c * 100 + 50, board_rect.y + r * 100 + 50))
                surface.blit(text, rect)
                
    winner = game.check_winner()
    if winner is not None:
        status = "Draw!" if winner == 0 else "X Wins!" if winner == 1 else "O Wins!"
        text = font.render(status, True, (0, 0, 0))
        surface.blit(text, (50, 650))
        
    # Draw instructional text
    instructions = [
        "Use Mouse Wheel / Drag to pan Tree",
        "Hover Nodes to see board state",
        "Green paths indicate Optimal Move",
        "Red nodes indicate Alpha-Beta Pruning"
    ]
    small_font = pygame.font.SysFont(None, 20)
    for idx, inst in enumerate(instructions):
        text_surf = small_font.render(inst, True, (100, 100, 100))
        surface.blit(text_surf, (20, 700 + idx * 20))

def main():
    clock = pygame.time.Clock()
    running = True
    ai_turn = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to visualizer and UI
            visualizer.process_event(event)
            
            if algo_toggle.handle_event(event): pass
            if mode_toggle.handle_event(event): pass
            
            if restart_btn.handle_event(event):
                game.reset()
                visualizer.set_tree(None)
                ai_turn = False
                
            # Handle board clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if board_rect.collidepoint(event.pos) and not ai_turn and game.check_winner() is None:
                    # Human vs AI mode
                    human_turn = mode_toggle.state # True = Human vs AI
                    if human_turn:
                        c = (event.pos[0] - board_rect.x) // 100
                        r = (event.pos[1] - board_rect.y) // 100
                        if game.make_move(r, c):
                            ai_turn = True

        mode = mode_toggle.state # True = H vs AI, False = AI vs AI
        
        # AI Logic execution
        if game.check_winner() is None:
            algo = "minimax" if algo_toggle.state else "alpha_beta"
            
            if not mode: # AI vs AI
                pygame.time.delay(500)
                # Render screen once before calculating so things don't freeze un-updated
                draw_board(screen)
                pygame.display.flip()
                
                move, tree_root = get_best_move(game, algo=algo, max_depth=4)
                if move:
                    game.make_move(move[0], move[1])
                    visualizer.set_tree(tree_root)
            
            elif mode and ai_turn: # Human vs AI, and it's AI's turn
                pygame.time.delay(10)
                draw_board(screen)
                pygame.display.flip()
                
                move, tree_root = get_best_move(game, algo=algo, max_depth=4)
                if move:
                    game.make_move(move[0], move[1])
                    visualizer.set_tree(tree_root)
                ai_turn = False

        # Drawing
        screen.fill((255, 255, 255))
        
        draw_board(screen)
        
        algo_toggle.draw(screen)
        mode_toggle.draw(screen)
        restart_btn.draw(screen)
        
        visualizer.draw(screen)
        
        pygame.display.flip()
        clock.tick(30)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
