import tkinter as tk
from collections import namedtuple

import game
import data
from colours import *
from font import ink_free


TieredStatistic = namedtuple("TieredStatistic", "bronze silver gold platinum")

WIN_STREAK_CATEGORIES = TieredStatistic(2, 5, 20, 78)


class MainMenu(tk.Frame):
    """
    The main menu of the application.
    This is displayed when the player launches the game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Main Menu")

        self.title_label = tk.Label(
            self, font=ink_free(100, True), text="Countdown")
        self.level_label_frame = LevelLabelFrame(self, 1, 0)
        
        streak = data.get_win_streak()
        self.win_streak_label = CurrentWinStreakLabel(self, streak)
        
        self.navigation_frame = MainMenuNavigationFrame(self)

        self.title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.level_label_frame.grid(row=1, column=0, pady=10, sticky="s")
        self.win_streak_label.grid(row=2, column=0, pady=10, sticky="n")
        self.navigation_frame.grid(
            row=1, column=1, rowspan=2, padx=10, sticky="n")
    
    def play(self) -> None:
        """
        Starts the game.
        """
        self.destroy()
        game.Game(self.root).pack()


class LevelLabelFrame(tk.LabelFrame):
    """
    Information about the player's current level and XP.
    """

    def __init__(
        self, master: MainMenu, level: int, xp: int | None = None) -> None:

        super().__init__(
            master, font=ink_free(25), text=f"Level {level}", labelanchor="n")

        if level < 100:
            self.progress_bar = LevelProgressBar(self, xp / level)
            self.progress_label = tk.Label(
                self, font=ink_free(15), text=f"{xp} / {level * 100} XP")
            
            self.progress_bar.pack()
            self.progress_label.pack()
        else:
            # Max Level (100)
            self.max_level_label = tk.Label(
                self, font=ink_free(20), text="Max Level!", fg=GREEN)        
            self.max_level_label.pack(padx=25, pady=25)
        

class LevelProgressBar(tk.Frame):
    """
    Visually shows how far the player is into a level.
    """

    def __init__(self, master: LevelLabelFrame, progress: float) -> None:
        super().__init__(master)

        green_width = int(progress * 2) # 1 width per 0.5% of progress.
        self.canvas = tk.Canvas(master, width=200, height=8)
        self.canvas.create_rectangle(0, 0, green_width, 8, fill=GREEN)
        self.canvas.create_rectangle(green_width, 0, 200, 8, fill=GREY)
        self.canvas.pack(padx=25, pady=25)


class CurrentWinStreakLabel(tk.Label):
    """
    Displays current win streak of the player in an appropriate
    way based on the streak length.
    """

    def __init__(self, master: MainMenu, streak: int) -> None:
        text = f"Current win streak: {streak}"
        colour = (
            BLACK if streak < WIN_STREAK_CATEGORIES.bronze else
            BRONZE if streak < WIN_STREAK_CATEGORIES.silver else
            SILVER if streak < WIN_STREAK_CATEGORIES.gold else
            GOLD if streak < WIN_STREAK_CATEGORIES.platinum else
            PLATINUM)
        
        super().__init__(
            master, font=ink_free(15, True), text=text, fg=colour, width=22)


class MainMenuNavigationFrame(tk.Frame):
    """
    A frame of buttons which allows the player to
    navigate through the app.
    """

    def __init__(self, master: MainMenu) -> None:
        super().__init__(master)

        self.play_button = tk.Button(
            self, font=ink_free(25, True), text="Play", relief="ridge",
            bg=ORANGE, activebackground=GREEN, width=10, border=10,
            command=master.play)
        self.stats_button = tk.Button(
            self, font=ink_free(15), text="Stats",
            bg=ORANGE, activebackground=GREEN, width=15, border=3)
        self.achievements_button = tk.Button(
            self, font=ink_free(15), text="Achievements",
            bg=ORANGE, activebackground=GREEN, width=15, border=3)
        self.history_button = tk.Button(
            self, font=ink_free(15), text="History",
            bg=ORANGE, activebackground=GREEN, width=15, border=3)
        self.options_button = tk.Button(
            self, font=ink_free(15), text="Options",
            bg=ORANGE, activebackground=GREEN, width=15, border=3)
        self.tutorial_button = tk.Button(
            self, font=ink_free(15), text="Tutorial",
            bg=ORANGE, activebackground=GREEN, width=15, border=3)
        self.credits_button = tk.Button(
            self, font=ink_free(15), text="Credits",
            bg=ORANGE, activebackground=GREEN, width=15, border=3)

        self.play_button.pack(pady=5)
        self.stats_button.pack(pady=5)
        self.achievements_button.pack(pady=5)
        self.history_button.pack(pady=5)
        self.options_button.pack(pady=5)
        self.tutorial_button.pack(pady=5)
        self.credits_button.pack(pady=5)