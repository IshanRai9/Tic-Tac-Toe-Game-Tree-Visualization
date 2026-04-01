import { useState, useEffect } from 'react';
import './App.css';

type Player = 1 | -1;
type BoardState = number[][];

interface TreeNodeData {
  board: BoardState;
  player: Player | null;
  move: [number, number] | null;
  score: number;
  is_pruned: boolean;
  alpha: number | 'inf' | '-inf';
  beta: number | 'inf' | '-inf';
  best_move: [number, number] | null;
  children: TreeNodeData[];
}

interface PositionedNode {
  id: string;
  x: number;
  y: number;
  data: TreeNodeData;
  isOptimalPath: boolean;
}

interface TreeEdge {
  id: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  isOptimal: boolean;
}

function MiniBoard({ board, isOptimal, isPruned }: { board: BoardState | null, isOptimal: boolean, isPruned: boolean, node: TreeNodeData }) {
  if (isPruned) {
    return <div className={`mini-board pruned`}><div className="node-info">Pruned</div></div>;
  }
  if (!board) return null;

  return (
    <div className={`mini-board ${isOptimal ? 'optimal' : ''}`}>
      {board.map((row, r) =>
        row.map((cell, c) => (
          <div key={`${r}-${c}`} className={`mini-cell ${cell === 1 ? 'X' : cell === -1 ? 'O' : ''}`}>
             {cell === 1 ? 'X' : cell === -1 ? 'O' : ''}
          </div>
        ))
      )}
    </div>
  );
}

function calculateLayout(
  root: TreeNodeData,
  width: number,
  startX: number = 0,
  startY: number = 50,
  levelHeight: number = 100
) {
  const nodes: PositionedNode[] = [];
  const edges: TreeEdge[] = [];
  let idCounter = 0;

  function traverse(node: TreeNodeData, left: number, right: number, y: number, parentX: number | null, parentY: number | null, optimalPath: boolean): [number, number] {
    const w = right - left;
    const x = left + w / 2;
    const currentId = `node-${idCounter++}`;
    
    nodes.push({ id: currentId, x, y, data: node, isOptimalPath: optimalPath });

    if (parentX !== null && parentY !== null) {
      edges.push({
        id: `edge-${currentId}`,
        x1: parentX,
        y1: parentY + 32,
        x2: x,
        y2: y,
        isOptimal: optimalPath
      });
    }

    if (node.children && node.children.length > 0) {
      const childW = w / node.children.length;
      node.children.forEach((child, idx) => {
        const cLeft = left + idx * childW;
        const cRight = cLeft + childW;
        const isOptimalChild = child.move && node.best_move && child.move[0] === node.best_move[0] && child.move[1] === node.best_move[1] && !child.is_pruned;
        traverse(child, cLeft, cRight, y + levelHeight, x, y, optimalPath && !!isOptimalChild);
      });
    }
    return [x, y];
  }

  function countLeaves(node: TreeNodeData): number {
    if (!node.children || node.children.length === 0) return 1;
    return node.children.reduce((acc, child) => acc + countLeaves(child), 0);
  }
  
  const totalLeaves = countLeaves(root);
  // Ensure we don't stretch unnecessarily; allocate realistic width per leaf.
  const treeWidth = Math.max(width, totalLeaves * 120);

  traverse(root, startX, treeWidth, startY, null, null, true);
  return { nodes, edges, calcWidth: treeWidth };
}

function App() {
  const [board, setBoard] = useState<BoardState>([
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
  ]);
  const [algo, setAlgo] = useState<string>('minimax');
  const [turn, setTurn] = useState<Player>(1);
  const [winner, setWinner] = useState<string | null>(null);
  const [treeContext, setTreeContext] = useState<TreeNodeData | null>(null);
  const [isAiComputing, setIsAiComputing] = useState(false);
  const [maxDepth, setMaxDepth] = useState<number>(6);

  const resetGame = () => {
    setBoard([[0, 0, 0], [0, 0, 0], [0, 0, 0]]);
    setTurn(1);
    setWinner(null);
    setTreeContext(null);
  };

  const handleCellClick = async (r: number, c: number) => {
    if (board[r][c] !== 0 || winner || turn !== 1 || isAiComputing) return;

    const newBoard = board.map(row => [...row]);
    newBoard[r][c] = 1;
    setBoard(newBoard);
    setTurn(-1);
  };

  useEffect(() => {
    if (turn === -1 && !winner) {
      fetchAiMove();
    }
  }, [board, turn, winner]);

  const fetchAiMove = async () => {
    setIsAiComputing(true);
    try {
      const resp = await fetch('http://localhost:8000/api/best_move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ board, player: -1, algo, max_depth: maxDepth })
      });
      const data = await resp.json();
      
      if (data.move) {
        const [r, c] = data.move;
        setBoard(prev => {
          const nm = prev.map(row => [...row]);
          nm[r][c] = -1;
          return nm;
        });
        setTurn(1);
      }
      if (data.tree) setTreeContext(data.tree);

    } catch(err) {
      console.error(err);
    }
    setIsAiComputing(false);
  };

  useEffect(() => {
    let draw = true;
    let win = null;
    const lines = [
      ...board,
      [board[0][0], board[1][0], board[2][0]], [board[0][1], board[1][1], board[2][1]], [board[0][2], board[1][2], board[2][2]],
      [board[0][0], board[1][1], board[2][2]], [board[0][2], board[1][1], board[2][0]]
    ];
    for (const l of lines) {
      if (l[0] !== 0 && l[0] === l[1] && l[1] === l[2]) {
        win = l[0];
      }
      if (l.includes(0)) draw = false;
    }
    if (win === 1) setWinner("You Win!");
    else if (win === -1) setWinner("AI Wins!");
    else if (draw) setWinner("Draw!");
  }, [board]);

  const { nodes, edges, calcWidth } = treeContext ? calculateLayout(treeContext, 800) : {nodes: [], edges: [], calcWidth: 0};

  return (
    <div className="dashboard">
      <div className="left-panel">
        <h1 className="title">Tic Tac Toe Visualizer</h1>
        
        <div className="board">
          {board.map((row, r) => row.map((cell, c) => (
             <div 
               key={`${r}-${c}`} 
               className={`cell ${cell === 1 ? 'X' : cell === -1 ? 'O' : ''}`}
               onClick={() => handleCellClick(r, c)}
             >
               {cell === 1 ? 'X' : cell === -1 ? 'O' : ''}
             </div>
          )))}
        </div>

        <div className="status">
          {winner ? winner : isAiComputing ? "AI is thinking..." : turn === 1 ? "Your Turn (X)" : "AI Turn (O)"}
        </div>

        <div className="controls">
          <label>
            Algorithm
            <select value={algo} onChange={e => { setAlgo(e.target.value); resetGame(); }}>
              <option value="minimax">Minimax</option>
              <option value="alpha_beta">Alpha-Beta Pruning</option>
            </select>
          </label>

          <label>
            Search Depth: {maxDepth}
            <input 
              type="range" 
              min="1" 
              max="9" 
              value={maxDepth} 
              onChange={e => setMaxDepth(parseInt(e.target.value))} 
            />
          </label>
          
          <button onClick={resetGame}>Restart Game</button>
        </div>
      </div>

      <div className="right-panel">
        {treeContext ? (
           <div className="tree-container" style={{ width: calcWidth, height: Math.max(...nodes.map(n => n.y), 800) + 100 }}>
             <svg className="tree-lines">
               {edges.map(e => (
                  <line 
                    key={e.id} 
                    x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2} 
                    stroke={e.isOptimal ? '#2dd4bf' : '#334155'} 
                    strokeWidth={e.isOptimal ? 3 : 1.5} 
                  />
               ))}
             </svg>
   
             {nodes.map(n => (
               <div key={n.id} className="node-group" style={{ left: n.x, top: n.y }}>
                 <MiniBoard board={n.data.board} isOptimal={n.isOptimalPath} isPruned={n.data.is_pruned} node={n.data} />
                 {!n.data.is_pruned && (
                    <div className="node-info">
                      Score: {n.data.score}
                      {algo === 'alpha_beta' && <><br/>A:{n.data.alpha} B:{n.data.beta}</>}
                    </div>
                 )}
               </div>
             ))}
           </div>
        ) : (
           <div style={{color: '#475569', textAlign: 'center', marginTop: '40vh', fontSize: '1.2rem'}}>
             Make a move to visualize the AI decision tree.
           </div>
        )}
      </div>
    </div>
  );
}

export default App;
