import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from game import TicTacToe
from ai import get_best_move

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoveRequest(BaseModel):
    board: list[list[int]]
    player: int
    algo: str
    max_depth: int = 4

@app.post("/api/best_move")
def get_best_move_endpoint(request: MoveRequest):
    game = TicTacToe()
    game.board = np.array(request.board)
    game.current_player = request.player
    
    move, tree_root = get_best_move(game, algo=request.algo, max_depth=request.max_depth)
    
    return {
        "move": [int(move[0]), int(move[1])] if move else None,
        "tree": tree_root.to_dict() if tree_root else None,
        "winner": game.check_winner() if hasattr(game, "check_winner") else None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
