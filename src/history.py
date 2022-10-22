import tkinter as tk

import menu
import data
import game
from font import ink_free
from colours import *
from utils import epoch_to_strftime


MAX_SOLUTION_DISPLAY_LENGTH = 36


class HistoryWindow(tk.Frame):
    """
    Where the player can view their past games
    (up to the 1000 most recent ones).
    This includes being able to generate solutions just
    like at the end of a game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - History")
        self.recent_games = data.get_game_data()[-1000:]
        self.recent_game_frame = None

        self.title_label = tk.Label(
            self, font=ink_free(50, True), text="History")

        self.recent_games_frame = RecentGamesFrame(self)
        
        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=self.back)
        
        self.title_label.grid(row=0, padx=10, pady=5)
        self.recent_games_frame.grid(row=1, padx=10, pady=5)
        self.back_button.grid(row=3, padx=10, pady=5)
    
    def select_game(self) -> None:
        """
        Get current game selection and display its data.
        """
        current_index = self.recent_games_frame.listbox.curselection()[0]
        # -1 means most recent (index 0).
        current_game = self.recent_games[-current_index-1]
        if self.recent_game_frame:
            self.recent_game_frame.destroy()
        self.recent_game_frame = GameDataLabelFrame(self, current_game)
        self.recent_game_frame.grid(row=2, padx=10, pady=5)
    
    def back(self) -> None:
        """
        Returns to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()


class RecentGamesFrame(tk.Frame):
    """
    Holds a listbox of recent games which can be
    vertically navigated with a scrollbar.
    """

    def __init__(self, master: HistoryWindow) -> None:
        super().__init__(master)
        self.listbox = tk.Listbox(
            self, font=ink_free(12), width=55, height=5,
            bg=GREEN, border=5)
        self.listbox.bind("<<ListboxSelect>>", lambda _: master.select_game())
        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        
        for game in master.recent_games:
            display = "{} | {} -> {} | {}".format(
                epoch_to_strftime(game["start_time"]),
                str(tuple(game["numbers"])), game["target"],
                "✔️" if game["is_win"] else "❌")
            self.listbox.insert(0, display)
        
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        
        self.listbox.pack(side="left")
        self.scrollbar.pack(side="right", fill="y")


class GameDataLabelFrame(tk.LabelFrame):
    """
    Holds the data of a recent game.
    """

    def __init__(self, master: HistoryWindow, game_data: dict) -> None:
        super().__init__(
            master, font=ink_free(15, True),
            text="Recent Game", labelanchor="n")
        self.data = game_data
        
        self.selected_numbers_frame = game.SelectedNumbersFrame(
            self, game_data["numbers"])
        self.target_number_label = game.TargetNumberLabel(
            self, game_data["target"])
        self.stats_frame = GameDataStatsFrame(self)
        
        self.selected_numbers_frame.grid(
            row=0, column=0, columnspan=3, padx=10, pady=5)
        self.target_number_label.grid(row=1, column=0, padx=10, pady=5)
        self.stats_frame.grid(row=1, column=1, padx=10, pady=5)


class GameDataStatsFrame(tk.Frame):
    """
    Holds the stats of a game, including:
    - Start time
    - Stop time
    - Outcome
    - Solution
    - XP earned
    - XP sources
    """

    def __init__(self, master: GameDataLabelFrame) -> None:
        super().__init__(master)
        start_time = epoch_to_strftime(master.data["start_time"])
        stop_time = epoch_to_strftime(master.data["stop_time"])
        outcome = "Win!" if master.data["is_win"] else "Loss"
        solution = master.data["solution"] or "N/A"
        if len(solution) > MAX_SOLUTION_DISPLAY_LENGTH:
            solution = "Too long to display!"
        xp_earned = master.data["xp_earned"]
        xp_sources = master.data["xp_sources"]

        self.stats_label = tk.Label(
            self, font=ink_free(15), width=45,
            text="\n".join(
                (
                    f"Start time: {start_time}", f"Finish time: {stop_time}",
                    f"Outcome: {outcome}", f"Solution: {solution}",
                    f"{xp_earned}XP earned")))
        self.xp_sources_frame = XpSourcesFrame(self, xp_sources)

        self.stats_label.pack(padx=10, pady=5, side="left")
        self.xp_sources_frame.pack(padx=10, pady=5, side="right")


class XpSourcesFrame(tk.Frame):
    """
    Holds the XP sources listbox along with a vertical scrollbar.
    """

    def __init__(
        self, master: GameDataStatsFrame, xp_sources: list[str]
    ) -> None:
        super().__init__(master)
        self.listbox = tk.Listbox(
            self, font=ink_free(15), width=25, height=5)
        for source in xp_sources:
            self.listbox.insert("end", source)
        self.scrollbar = tk.Scrollbar(self, orient="vertical")

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side="left")
        self.scrollbar.pack(side="right", fill="y")