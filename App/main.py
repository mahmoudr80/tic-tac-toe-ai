import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Core.game import Game
from Util.constants import HUMAN_PLAYER_VALUE, AI_PLAYER_VALUE, SYMBOL_X, SYMBOL_O

class GomokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku AI - Complete Implementation")
        self.root.geometry("600x700")

        self.difficulty = tk.StringVar(value="medium")
        self.heuristic = tk.IntVar(value=1)
        self.grid_size = tk.IntVar(value=15)
        self.alpha_beta = tk.BooleanVar(value=True)

        self.game = None
        self.board_buttons = []
        self.status_label = None

        self.create_setup_menu()

    def create_setup_menu(self):
        # Main Frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(main_frame, text="🎮 Gomoku AI", font=("Arial", 24, "bold"))
        title.pack(pady=10)

        # Settings Frame
        settings_frame = tk.LabelFrame(main_frame, text="Game Settings", padx=20, pady=20)
        settings_frame.pack(pady=10, fill=tk.X)

        # Difficulty
        tk.Label(settings_frame, text="Difficulty Level:", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=5)
        diff = ttk.Combobox(settings_frame, textvariable=self.difficulty, state="readonly", width=20)
        diff["values"] = ("easy", "medium", "hard")
        diff.grid(row=0, column=1, pady=5)

        # Heuristic
        tk.Label(settings_frame, text="Heuristic Function:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        heur_frame = tk.Frame(settings_frame)
        heur_frame.grid(row=1, column=1, pady=5)
        
        tk.Radiobutton(heur_frame, text="No Heuristic", variable=self.heuristic, value=0).pack(anchor=tk.W)
        tk.Radiobutton(heur_frame, text="Heuristic 1 (Simple Count)", variable=self.heuristic, value=1).pack(anchor=tk.W)
        tk.Radiobutton(heur_frame, text="Heuristic 2 (Pattern-Based)", variable=self.heuristic, value=2).pack(anchor=tk.W)

        # Alpha-Beta Pruning
        tk.Label(settings_frame, text="Alpha-Beta Pruning:", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
        alpha_check = tk.Checkbutton(settings_frame, text="Enable Alpha-Beta Pruning", variable=self.alpha_beta)
        alpha_check.grid(row=2, column=1, pady=5, sticky=tk.W)

        # Board Size
        tk.Label(settings_frame, text="Board Size:", font=("Arial", 11)).grid(row=3, column=0, sticky=tk.W, pady=5)
        size_frame = tk.Frame(settings_frame)
        size_frame.grid(row=3, column=1, pady=5)
        size_entry = ttk.Spinbox(size_frame, from_=5, to=19, textvariable=self.grid_size, width=10)
        size_entry.pack(side=tk.LEFT)
        tk.Label(size_frame, text="x").pack(side=tk.LEFT, padx=5)
        size_label = tk.Label(size_frame, textvariable=self.grid_size)
        size_label.pack(side=tk.LEFT)

        # Info Frame
        info_frame = tk.LabelFrame(main_frame, text="Configuration Summary", padx=20, pady=10)
        info_frame.pack(pady=10, fill=tk.X)

        # Start Button
        start_btn = tk.Button(main_frame, text="▶️ Start Game", command=self.start_game, 
                             font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", 
                             padx=20, pady=10, cursor="hand2")
        start_btn.pack(pady=20)

    def start_game(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.game = Game(
            board_size=self.grid_size.get(),
            ai_difficulty=self.difficulty.get(),
            heuristic=self.heuristic.get(),
            use_alpha_beta=self.alpha_beta.get()
        )

        self.board_buttons = []
        self.create_game_ui()

    def create_game_ui(self):
        # Top Frame for info
        info_frame = tk.Frame(self.root, bg="#34495e", pady=10)
        info_frame.pack(fill=tk.X)

        config_text = f"Difficulty: {self.difficulty.get().upper()} | Heuristic: {self.heuristic.get()} | Alpha-Beta: {'ON' if self.alpha_beta.get() else 'OFF'}"
        tk.Label(info_frame, text=config_text, font=("Arial", 10), bg="#34495e", fg="white").pack()

        self.status_label = tk.Label(info_frame, text="Your Turn (O)", font=("Arial", 12, "bold"), 
                                     bg="#34495e", fg="#3498db")
        self.status_label.pack(pady=5)

        # Board Frame
        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=10)

        # Create board
        for i in range(self.game.board.size):
            row_button = []
            for j in range(self.game.board.size):
                btn = tk.Button(
                    board_frame, text=" ", width=3, height=1,
                    command=lambda r=i, c=j: self.on_move(r, c),
                    font=("Arial", 12, "bold"),
                    bg="#ecf0f1",
                    activebackground="#bdc3c7"
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                row_button.append(btn)
            self.board_buttons.append(row_button)

        # Stats Frame
        stats_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        stats_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(stats_frame, text="🔄 New Game", command=self.restart_game, 
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack()

    def on_move(self, row, col):
        if self.game.play_turn(row, col):
            self.update_ui()
            if self.game.is_game_over():
                self.display_winner()
            elif self.game.current_player == AI_PLAYER_VALUE:
                self.status_label.config(text="AI is thinking...", fg="#e74c3c")
                self.root.update()
                self.root.after(300, self.ai_move)

    def ai_move(self):
        self.game.play_turn(None, None)
        self.update_ui()
        if self.game.is_game_over():
            self.display_winner()
        else:
            self.status_label.config(text="Your Turn (O)", fg="#3498db")

    def update_ui(self):
        for i in range(self.game.board.size):
            for j in range(self.game.board.size):
                v = self.game.board.board[i][j]
                if v == HUMAN_PLAYER_VALUE:
                    self.board_buttons[i][j].config(text=SYMBOL_O, bg="#3498db", fg="white")
                elif v == AI_PLAYER_VALUE:
                    self.board_buttons[i][j].config(text=SYMBOL_X, bg="#e74c3c", fg="white")

    def display_winner(self):
        winner = self.game.board.check_winner()
        stats = self.game.get_statistics()
        
        if winner == 0:
            msg = "🤝 It's a Draw!"
        elif winner == AI_PLAYER_VALUE:
            msg = "🤖 AI Wins!"
        else:
            msg = "🎉 You Win!"

        if stats:
            msg += f"\n\n📊 Game Statistics:\n"
            msg += f"AI Moves: {stats['total_moves']}\n"
            msg += f"Avg Time/Move: {stats['avg_time']:.3f}s\n"
            msg += f"Total Time: {stats['total_time']:.2f}s\n"
            msg += f"Avg Nodes Explored: {stats['avg_nodes']:.0f}\n"
            msg += f"Total Nodes: {stats['total_nodes']}"

        messagebox.showinfo("Game Over", msg)
        self.root.after(1000, self.restart_game)

    def restart_game(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.create_setup_menu()

if __name__ == "__main__":
    root = tk.Tk()
    app = GomokuApp(root)
    root.mainloop()