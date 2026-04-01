import numpy as np
import math

class TreeNode:
    def __init__(self, board, player, move=None):
        self.board = board
        self.player = player # The player who JUST made the move (-1 or 1)
        self.move = move # (row, col) that led to this board state
        self.children = []
        self.score = 0
        self.is_pruned = False
        self.alpha = -math.inf
        self.beta = math.inf
        self.best_move = None
        self.x = 0
        self.y = 0
        
    def add_child(self, child_node):
        self.children.append(child_node)

    def to_dict(self):
        return {
            "board": self.board.tolist() if self.board is not None else None,
            "player": self.player,
            "move": [int(self.move[0]), int(self.move[1])] if self.move else None,
            "score": float(self.score),
            "is_pruned": self.is_pruned,
            "alpha": "inf" if self.alpha == float('inf') else "-inf" if self.alpha == float('-inf') else float(self.alpha),
            "beta": "inf" if self.beta == float('inf') else "-inf" if self.beta == float('-inf') else float(self.beta),
            "best_move": [int(self.best_move[0]), int(self.best_move[1])] if self.best_move else None,
            "children": [child.to_dict() for child in self.children]
        }

def get_best_move(game, algo="minimax", max_depth=4):
    """
    Wrapper function to get the best move and the generated decision tree.
    """
    root_val = game.current_player * -1
    root = TreeNode(np.copy(game.board), root_val, None)
    is_maximizing = (game.current_player == 1)
    
    if algo == "minimax":
        score, move = minimax(game, 0, is_maximizing, max_depth, root)
    else:
        score, move = alpha_beta(game, 0, -math.inf, math.inf, is_maximizing, max_depth, root)
        
    return move, root

def minimax(game, depth, is_maximizing, max_depth=4, current_node=None):
    winner = game.check_winner()
    
    if winner is not None:
        if winner == 1: current_node.score = 10 - depth
        elif winner == -1: current_node.score = -10 + depth
        else: current_node.score = 0
        return current_node.score, None
        
    if depth >= max_depth:
        # Evaluate board heuristically or return 0 for max depth
        current_node.score = 0
        return current_node.score, None
        
    valid_moves = game.get_valid_moves()
    
    if is_maximizing:
        best_score = -math.inf
        best_move = None
        for move in valid_moves:
            game.make_move(move[0], move[1])
            child_node = TreeNode(np.copy(game.board), game.current_player * -1, move)
            current_node.add_child(child_node)
            
            score, _ = minimax(game, depth + 1, False, max_depth, child_node)
            game.undo_move(move[0], move[1])
            
            if score > best_score:
                best_score = score
                best_move = move
                
        current_node.score = best_score
        current_node.best_move = best_move
        return best_score, best_move
    else:
        best_score = math.inf
        best_move = None
        for move in valid_moves:
            game.make_move(move[0], move[1])
            child_node = TreeNode(np.copy(game.board), game.current_player * -1, move)
            current_node.add_child(child_node)
            
            score, _ = minimax(game, depth + 1, True, max_depth, child_node)
            game.undo_move(move[0], move[1])
            
            if score < best_score:
                best_score = score
                best_move = move
                
        current_node.score = best_score
        current_node.best_move = best_move
        return best_score, best_move

def alpha_beta(game, depth, alpha, beta, is_maximizing, max_depth=4, current_node=None):
    current_node.alpha = alpha
    current_node.beta = beta
    
    winner = game.check_winner()
    if winner is not None:
        if winner == 1: current_node.score = 10 - depth
        elif winner == -1: current_node.score = -10 + depth
        else: current_node.score = 0
        return current_node.score, None
        
    if depth >= max_depth:
        current_node.score = 0
        return current_node.score, None
        
    valid_moves = game.get_valid_moves()
    
    if is_maximizing:
        best_score = -math.inf
        best_move = None
        for move in valid_moves:
            game.make_move(move[0], move[1])
            child_node = TreeNode(np.copy(game.board), game.current_player * -1, move)
            current_node.add_child(child_node)
            
            score, _ = alpha_beta(game, depth + 1, alpha, beta, False, max_depth, child_node)
            game.undo_move(move[0], move[1])
            
            if score > best_score:
                best_score = score
                best_move = move
                
            alpha = max(alpha, best_score)
            current_node.alpha = alpha
            
            if beta <= alpha:
                pruned_node = TreeNode(None, None, None)
                pruned_node.is_pruned = True
                current_node.add_child(pruned_node)
                break
                
        current_node.score = best_score
        current_node.best_move = best_move
        return best_score, best_move
    else:
        best_score = math.inf
        best_move = None
        for move in valid_moves:
            game.make_move(move[0], move[1])
            child_node = TreeNode(np.copy(game.board), game.current_player * -1, move)
            current_node.add_child(child_node)
            
            score, _ = alpha_beta(game, depth + 1, alpha, beta, True, max_depth, child_node)
            game.undo_move(move[0], move[1])
            
            if score < best_score:
                best_score = score
                best_move = move
                
            beta = min(beta, best_score)
            current_node.beta = beta
            
            if beta <= alpha:
                pruned_node = TreeNode(None, None, None)
                pruned_node.is_pruned = True
                current_node.add_child(pruned_node)
                break
                
        current_node.score = best_score
        current_node.best_move = best_move
        return best_score, best_move
