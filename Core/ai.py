import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Util.constants import HUMAN_PLAYER_VALUE, AI_PLAYER_VALUE

class AI:
    def __init__(self, difficulty="medium", heuristic=1, use_alpha_beta=True):
        self.difficulty_levels = {"easy": 2, "medium": 3, "hard": 4}
        self.depth = self.difficulty_levels.get(difficulty, 4)
        
        # heuristic: 0 = no heuristic, 1 = heuristic1, 2 = heuristic2
        self.heuristic = heuristic
        self.use_alpha_beta = use_alpha_beta
        self.nodes_explored = 0  # للتحليل والمقارنة

    # -----------------------------
    # HEURISTIC 1: Simple Count
    # -----------------------------
    def heuristic1(self, board):
        # Faster simple count: weight contiguous runs more heavily.
        ai_score = 0
        human_score = 0
        size = board.size

        # scan rows, cols and diagonals for contiguous runs
        def scan_line(get_cell, length):
            a = 0
            h = 0
            run_ai = 0
            run_h = 0
            for i in range(length):
                v = get_cell(i)
                if v == AI_PLAYER_VALUE:
                    run_ai += 1
                    if run_h:
                        h += run_h
                        run_h = 0
                elif v == HUMAN_PLAYER_VALUE:
                    run_h += 1
                    if run_ai:
                        a += run_ai
                        run_ai = 0
                else:
                    if run_ai:
                        a += run_ai
                        run_ai = 0
                    if run_h:
                        h += run_h
                        run_h = 0
            # flush
            a += run_ai
            h += run_h
            return a, h

        # rows
        for x in range(size):
            a, h = scan_line(lambda i: board.board[x][i], size)
            ai_score += a
            human_score += h

        # cols
        for y in range(size):
            a, h = scan_line(lambda i: board.board[i][y], size)
            ai_score += a
            human_score += h

        return ai_score - human_score

    # -----------------------------
    # HEURISTIC 2: Pattern-Based
    # -----------------------------
    def heuristic2(self, board):
        # Optimized pattern scoring: avoid list allocations and repeated counts.
        def score_window(get_cell):
            ai = 0
            hu = 0
            empty = 0
            for k in range(5):
                v = get_cell(k)
                if v == AI_PLAYER_VALUE:
                    ai += 1
                elif v == HUMAN_PLAYER_VALUE:
                    hu += 1
                else:
                    empty += 1

            # lines that contain both players are less interesting
            if ai > 0 and hu > 0:
                return 0

            if ai == 5:
                return 100000
            if hu == 5:
                return -100000

            if ai == 4 and empty == 1:
                return 10000
            if hu == 4 and empty == 1:
                return -10000

            if ai == 3 and empty == 2:
                return 1000
            if hu == 3 and empty == 2:
                return -1000

            if ai == 2 and empty == 3:
                return 100
            if hu == 2 and empty == 3:
                return -100

            return 0

        total_score = 0
        size = board.size

        # horizontal and vertical
        for i in range(size):
            for j in range(size - 4):
                # horizontal window starting at (i,j)
                total_score += score_window(lambda k, ii=i, jj=j: board.board[ii][jj + k])
                # vertical window starting at (j,i)
                total_score += score_window(lambda k, ii=j, jj=i: board.board[ii + k][jj])

        # diagonals
        for i in range(size - 4):
            for j in range(size - 4):
                total_score += score_window(lambda k, ii=i, jj=j: board.board[ii + k][jj + k])
                total_score += score_window(lambda k, ii=i, jj=j: board.board[ii + k][jj + 4 - k])

        return total_score

    # -----------------------------
    # Evaluation Function
    # -----------------------------
    def evaluate(self, board):
        if self.heuristic == 0:
            # No heuristic - only terminal states have value
            return 0
        elif self.heuristic == 1:
            return self.heuristic1(board)
        elif self.heuristic == 2:
            return self.heuristic2(board)
        return 0

    # -----------------------------
    # MINIMAX WITHOUT ALPHA-BETA
    # -----------------------------
    def minimax_no_pruning(self, board, depth, maximizing):
        self.nodes_explored += 1
        
        winner = board.check_winner()
        if winner == AI_PLAYER_VALUE:
            return 10000, None
        elif winner == HUMAN_PLAYER_VALUE:
            return -10000, None
        elif winner == 0 or depth == 0:
            return self.evaluate(board), None

        best_move = None
        valid_moves = self.get_valid_moves(board)

        if maximizing:
            max_eval = -float('inf')
            for move in valid_moves:
                board.place_marker(move[0], move[1], AI_PLAYER_VALUE)
                evaluation, _ = self.minimax_no_pruning(board, depth-1, False)
                board.undo_move(move[0], move[1])

                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                board.place_marker(move[0], move[1], HUMAN_PLAYER_VALUE)
                evaluation, _ = self.minimax_no_pruning(board, depth-1, True)
                board.undo_move(move[0], move[1])

                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
            return min_eval, best_move

    # -----------------------------
    # MINIMAX WITH ALPHA-BETA PRUNING
    # -----------------------------
    def minimax_alpha_beta(self, board, depth, maximizing, alpha=-float('inf'), beta=float('inf')):
        self.nodes_explored += 1
        
        winner = board.check_winner()
        if winner == AI_PLAYER_VALUE:
            return 10000, None
        elif winner == HUMAN_PLAYER_VALUE:
            return -10000, None
        elif winner == 0 or depth == 0:
            return self.evaluate(board), None

        best_move = None
        valid_moves = self.get_valid_moves(board)

        if maximizing:
            max_eval = -float('inf')
            for move in valid_moves:
                board.place_marker(move[0], move[1], AI_PLAYER_VALUE)
                evaluation, _ = self.minimax_alpha_beta(board, depth-1, False, alpha, beta)
                board.undo_move(move[0], move[1])

                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move

                alpha = max(alpha, evaluation)
                if beta <= alpha:  # Alpha-Beta Pruning
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                board.place_marker(move[0], move[1], HUMAN_PLAYER_VALUE)
                evaluation, _ = self.minimax_alpha_beta(board, depth-1, True, alpha, beta)
                board.undo_move(move[0], move[1])

                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move

                beta = min(beta, evaluation)
                if beta <= alpha:  # Alpha-Beta Pruning
                    break
            return min_eval, best_move

    # -----------------------------
    # MAIN ENTRY POINT
    # -----------------------------
    def get_best_move(self, board):
        self.nodes_explored = 0  # Reset counter
        
        if self.use_alpha_beta:
            _, best_move = self.minimax_alpha_beta(board, self.depth, True)
        else:
            _, best_move = self.minimax_no_pruning(board, self.depth, True)
        
        return best_move

    # -----------------------------
    # VALID MOVES GENERATION
    # -----------------------------
    def get_valid_moves(self, board):
        moves = set()
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

        # Find moves near existing pieces
        for x in range(board.size):
            for y in range(board.size):
                if board.board[x][y] != 0:
                    for dx, dy in directions:
                        for step in range(1, 3):  # Extended to 2 steps
                            nx = x + dx * step
                            ny = y + dy * step
                            if 0 <= nx < board.size and 0 <= ny < board.size:
                                if board.board[nx][ny] == 0:
                                    moves.add((nx, ny))

        # If board is empty, start in center
        if not moves:
            return [(board.size // 2, board.size // 2)]

        # Score candidate moves locally to order and limit branching.
        moves_list = list(moves)

        def window_score_at(get_cell):
            ai = 0
            hu = 0
            empty = 0
            for k in range(5):
                v = get_cell(k)
                if v == AI_PLAYER_VALUE:
                    ai += 1
                elif v == HUMAN_PLAYER_VALUE:
                    hu += 1
                else:
                    empty += 1

            if ai > 0 and hu > 0:
                return 0
            if ai == 5:
                return 100000
            if hu == 5:
                return -100000
            if ai == 4 and empty == 1:
                return 10000
            if hu == 4 and empty == 1:
                return -10000
            if ai == 3 and empty == 2:
                return 1000
            if hu == 3 and empty == 2:
                return -1000
            if ai == 2 and empty == 3:
                return 100
            if hu == 2 and empty == 3:
                return -100
            return 0

        def score_move_local(x, y):
            # consider windows of length 5 in 4 directions that include (x,y)
            s = 0
            size = board.size

            # helper to safely read cell with simulated move value
            def cell_val(i, j, sim_player=None):
                if i == x and j == y:
                    return sim_player
                return board.board[i][j]

            dirs = [ (0,1), (1,0), (1,1), (1,-1) ]
            for dx, dy in dirs:
                # window offsets so that (x,y) is at position offset within 0..4
                for off in range(-4, 1):
                    cells = []
                    valid = True
                    for k in range(5):
                        nx = x + (off + k) * dx
                        ny = y + (off + k) * dy
                        if nx < 0 or ny < 0 or nx >= size or ny >= size:
                            valid = False
                            break
                        cells.append((nx, ny))
                    if not valid:
                        continue

                    # score as if AI plays here
                    s += window_score_at(lambda k, cs=cells: cell_val(cs[k][0], cs[k][1], AI_PLAYER_VALUE))
                    # also consider opponent threat (human plays here)
                    s += 0.9 * abs(window_score_at(lambda k, cs=cells: cell_val(cs[k][0], cs[k][1], HUMAN_PLAYER_VALUE)))

            return s

        scored = []
        for m in moves_list:
            scored.append((m, score_move_local(m[0], m[1])))

        # choose top-K moves based on depth (lower depth -> fewer moves)
        move_limit_map = {2: 6, 3: 12, 4: 30}
        limit = move_limit_map.get(self.depth, 12)

        scored.sort(key=lambda t: t[1], reverse=True)
        top = [m for m, _ in scored[:max(1, min(limit, len(scored)))] ]
        return top