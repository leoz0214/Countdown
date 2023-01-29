"""
The main menu which leads to different parts of the app.
"""
import tkinter as tk
import webbrowser
from pathlib import Path

import game
from mechanics import achievements
from mechanics import history
from mechanics import level
from mechanics import options
from mechanics import stats
from utils.colours import *
from utils.utils import ink_free, bool_to_state, get_music


WIN_STREAK_CATEGORIES = achievements.AchievementTierRequirements(2, 5, 20, 78)
MENU_MUSIC = get_music("menu.mp3")
TUTORIAL_FILE = f"{Path('').parent.absolute()}/TUTORIAL.html"


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
        self.navigation_frame = MainMenuNavigationFrame(self)

        player_options = options.get_options()
        if player_options["music"]["on"]:
            MENU_MUSIC.play(-1)

        if player_options["stats"]:
            self.level_label_frame = level.LevelLabelFrame(
                self, level.Level())

            streak = stats.get_win_streak()
            self.win_streak_label = CurrentWinStreakLabel(self, streak)

            self.title_label.grid(
                row=0, column=0, columnspan=2, padx=25, pady=15)
            self.level_label_frame.grid(row=1, column=0, pady=10, sticky="s")
            self.win_streak_label.grid(row=2, column=0, pady=10, sticky="n")
            self.navigation_frame.grid(
                row=1, column=1, rowspan=2, pady=15, sticky="n")
        else:
            self.title_label.pack(padx=25, pady=15)
            self.navigation_frame.pack(padx=10, pady=15)

    def exit(self) -> None:
        """
        Exits to another part of the application.
        """
        MENU_MUSIC.stop()
        self.destroy()

    def play(self) -> None:
        """
        Starts the game.
        """
        self.exit()
        game.Game(self.root).pack()

    def statistics(self) -> None:
        """
        Opens statistics.
        """
        self.exit()
        stats.StatisticsWindow(self.root).pack()

    def history(self) -> None:
        """
        Opens history.
        """
        self.exit()
        history.HistoryWindow(self.root).pack()

    def achievements(self) -> None:
        """
        Opens achievements.
        """
        self.exit()
        achievements.AchievementsWindow(self.root).pack()

    def options(self) -> None:
        """
        Opens options.
        """
        self.exit()
        options.OptionsWindow(self.root).pack()

    def tutorial(self) -> None:
        """
        Opens the tutorial of the game in a web browser.
        """
        webbrowser.open(TUTORIAL_FILE)


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
            GOLD if streak < WIN_STREAK_CATEGORIES.platinum else PLATINUM)
        super().__init__(
            master, font=ink_free(15, True), text=text, fg=colour, width=22)


class MainMenuNavigationFrame(tk.Frame):
    """
    Buttons which allow the player to navigate through the app.
    """

    def __init__(self, master: MainMenu) -> None:
        super().__init__(master)
        stats_on = options.get_option("stats")

        self.play_button = tk.Button(
            self, font=ink_free(25, True), text="Play", relief="ridge",
            bg=ORANGE, activebackground=GREEN, width=10, border=10,
            command=master.play)
        self.stats_button = tk.Button(
            self, font=ink_free(15), text="Stats",
            bg=ORANGE, activebackground=GREEN, width=15, border=3,
            command=master.statistics, state=bool_to_state(stats_on))
        self.achievements_button = tk.Button(
            self, font=ink_free(15), text="Achievements",
            bg=ORANGE, activebackground=GREEN, width=15, border=3,
            command=master.achievements, state=bool_to_state(stats_on))
        self.history_button = tk.Button(
            self, font=ink_free(15), text="History",
            bg=ORANGE, activebackground=GREEN, width=15, border=3,
            command=master.history, state=bool_to_state(stats_on))
        self.options_button = tk.Button(
            self, font=ink_free(15), text="Options", activebackground=GREEN,
            bg=ORANGE, width=15, border=3, command=master.options)
        self.tutorial_button = tk.Button(
            self, font=ink_free(15), text="Tutorial", activebackground=GREEN,
            bg=ORANGE, width=15, border=3, command=master.tutorial)

        self.play_button.pack(pady=5)
        self.stats_button.pack(pady=5)
        self.achievements_button.pack(pady=5)
        self.history_button.pack(pady=5)
        self.options_button.pack(pady=5)
        self.tutorial_button.pack(pady=5)
