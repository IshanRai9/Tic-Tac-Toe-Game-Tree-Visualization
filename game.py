import numpy as np

class TicTacToe:
    def __init__(self):
        # 0 = empty, 1 = X, -1 = O
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 1 # 1 for X, -1 for O
    
    def reset(self):
        self.board.fill(0)
        self.current_player = 1
    
    def get_valid_moves(self):
        return list(zip(*np.where(self.board == 0)))
    
    def make_move(self, row, col):
        if self.board[row][col] == 0:
            self.board[row][col] = self.current_player
            self.current_player *= -1
            return True
        return False
    
    def undo_move(self, row, col):
        self.board[row][col] = 0
        self.current_player *= -1
    
    def check_winner(self):
        """Returns 1 if X wins, -1 if O wins, 0 if draw, None if ongoing."""
        # Check rows
        row_sum = np.sum(self.board, axis=1)
        if 3 in row_sum: return 1
        if -3 in row_sum: return -1
        
        # Check cols
        col_sum = np.sum(self.board, axis=0)
        if 3 in col_sum: return 1
        if -3 in col_sum: return -1
        
        # Check diagonals
        diag1 = np.trace(self.board)
        diag2 = np.trace(np.fliplr(self.board))
        if diag1 == 3 or diag2 == 3: return 1
        if diag1 == -3 or diag2 == -3: return -1
        
        # Check draw
        if not np.any(self.board == 0):
            return 0  # Draw
            
        return None  # Game ongoing
        
    def is_game_over(self):
        return self.check_winner() is not None
