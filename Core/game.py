import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Core.board import Board
from Util.constants import HUMAN_PLAYER_VALUE, AI_PLAYER_VALUE
from Core.ai import AI
import time

class Game:
    def __init__(self, board_size=15, ai_difficulty="medium", heuristic=1, use_alpha_beta=True):
        self.board = Board(size=board_size)
        self.current_player = HUMAN_PLAYER_VALUE
        self.ai_difficulty = ai_difficulty
        self.heuristic = heuristic
        self.use_alpha_beta = use_alpha_beta
        
        # للتحليل والمقارنة
        self.move_times = []
        self.nodes_explored_list = []
        self.ai_moves_count = 0

    def play_turn(self, x, y):
        if self.current_player == HUMAN_PLAYER_VALUE:
            if self.board.place_marker(x, y, self.current_player):
                self.current_player = AI_PLAYER_VALUE
                return True
        else:
            ai = AI(self.ai_difficulty, heuristic=self.heuristic, use_alpha_beta=self.use_alpha_beta)
            
            # قياس الوقت والـ nodes explored
            start_time = time.time()
            move = ai.get_best_move(self.board)
            end_time = time.time()
            
            if move:
                self.board.place_marker(move[0], move[1], self.current_player)
                self.current_player = HUMAN_PLAYER_VALUE
                
                # حفظ البيانات للتحليل
                self.move_times.append(end_time - start_time)
                self.nodes_explored_list.append(ai.nodes_explored)
                self.ai_moves_count += 1
                
                return True
        return False

    def is_game_over(self):
        return self.board.check_winner() is not None
    
    def get_statistics(self):
        """للحصول على إحصائيات الأداء"""
        if not self.move_times:
            return None
        
        return {
            'total_moves': self.ai_moves_count,
            'avg_time': sum(self.move_times) / len(self.move_times),
            'total_time': sum(self.move_times),
            'avg_nodes': sum(self.nodes_explored_list) / len(self.nodes_explored_list) if self.nodes_explored_list else 0,
            'total_nodes': sum(self.nodes_explored_list)
        }