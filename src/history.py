"""
Displays recent games and allows the player to view their data
and also generate solutions for the recent games.
"""
import tkinter as tk

import menu
import data
import game
import solutions
from colours import *
from utils import epoch_to_strftime, ink_free


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
        self.recent_games = data.get_game_data()[-data.MAX_ALLOWED_GAME_DATA:]

        self.title_label = tk.Label(
            self, font=ink_free(50, True), text="History")
        self.back_button = tk.Button(
            self, font=ink_free(15), text="Back", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=self.back)

        if self.recent_games:
            self.recent_game_frame = None
            self.solutions_frame = None

            self.recent_games_frame = RecentGamesFrame(self)
            
            self.title_label.grid(row=0, padx=10)
            self.recent_games_frame.grid(row=1, padx=10, pady=5)
            self.back_button.grid(row=3, padx=10, pady=5)
        else:
            self.message_label = tk.Label(
                self, font=ink_free(75),
                text="No history yet!\nPlay a round!", fg=RED)
            self.back_button.config(font=ink_free(25))
            
            self.title_label.pack(padx=100, pady=25)
            self.message_label.pack(padx=100, pady=25)
            self.back_button.pack(padx=100, pady=25)

    def select_game(self) -> None:
        """
        Get current game selection and display its data.
        """
        current_index = self.recent_games_frame.listbox.curselection()[0]
        # -1 means most recent (index 0).
        current_game = self.recent_games[-current_index-1]
        if self.recent_game_frame:
            self.recent_game_frame.destroy()
        if self.solutions_frame:
            self.solutions_frame.destroy()
        self.recent_game_frame = GameDataLabelFrame(self, current_game)
        self.solutions_frame = solutions.SolutionsFrame(
            self.root, self, current_game["numbers"], current_game["target"])
        self.recent_game_frame.grid(row=2, padx=10, pady=5)

    def solutions(self) -> None:
        """
        Allows the player to generate solutions for the past game.
        """
        self.pack_forget()
        self.solutions_frame.pack()
        self.root.title("Countdown - History - Solutions")
    
    def exit_solutions(self) -> None:
        """
        Returns to the main game over screen upon
        leaving solution generation.
        """
        solutions.SOLUTION_FOUND_SFX.stop()
        solutions.NO_SOLUTION_FOUND_SFX.stop()
        if self.solutions_frame.settings:
            self.solutions_frame.cancel()
        self.solutions_frame.pack_forget()
        self.root.title("Countdown - History")
        self.pack()
    
    def close(self) -> None:
        """
        Deselects the current recent game from the listbox
        and destroys the data label frame.
        """
        self.recent_games_frame.listbox.select_clear(0, "end")
        self.recent_game_frame.destroy()
        self.solutions_frame.destroy()
    
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
        self.navigation_frame = GameDataNavigationFrame(self)
        
        self.selected_numbers_frame.grid(
            row=0, column=0, columnspan=2, padx=10, pady=5)
        self.target_number_label.grid(row=1, rowspan=2, column=0, padx=10)
        self.stats_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=5)
        self.navigation_frame.grid(row=2, column=1, padx=10, pady=5)


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


class GameDataNavigationFrame(tk.Frame):
    """
    Navigation for the game data label frame.
    """

    def __init__(self, master: GameDataLabelFrame) -> None:
        super().__init__(master)
        self.close_button = tk.Button(
            self, font=ink_free(20), text="Close", width=15, border=5,
            bg=ORANGE, activebackground=RED, command=master.master.close)
        self.solutions_button = tk.Button(
            self, font=ink_free(20), text="Solutions", width=15, border=5,
            bg=ORANGE, activebackground=GREEN,
            command=master.master.solutions)
        
        self.close_button.pack(padx=10, side="left")
        self.solutions_button.pack(padx=10, side="right")