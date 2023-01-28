"""
Displays recent games and allows the player to view their data
and also generate solutions for the recent games.
"""
import gzip
import os
import shutil
import time
import tkinter as tk
from contextlib import suppress

try:
    # Data intensive - quick JSON read-write speeds needed.
    import ujson as json
except ImportError:
    print("ujson unavailable, using json instead.")
    import json

import game
import menu
from utils.colours import *
from utils.io import check_folder_exists, FOLDER
from utils.utils import epoch_to_strftime, ink_free, days_to_seconds
from . import solutions


MAX_SOLUTION_DISPLAY_LENGTH = 36

GAME_DATA_FOLDER = f"{FOLDER}/game_data"
# Split game data into multiple files, so only a fairly small chunk
# of data has to be rewritten to add new data.
MAX_GAME_DATA_PER_FILE = 100
# Number of recent games which can be stored without time limit.
# Beyond that, game data older than 30 days is deleted.
MAX_ALLOWED_GAME_DATA = 1000


def remove_expired_games(
    files: list[str], final_file_check_limit: int) -> list[str]:
    """
    Removes expired games (ones that finished more than 30 days ago).
    Games older than 30 days are allowed if there are not too many.
    Returns new files (may be the same if no deletion required).
    Games are sorted by time, so a binary search for the boundary
    between expired and valid games (if any) can be found in O(log n).
    """
    index = len(files) // 2
    current_timestamp = time.time()
    found_expired = False
    final = files[-1]
    # Check is complete once the the loop is exited.
    while True:
        with gzip.open(files[index], "rt", encoding="utf8") as f:
            data = json.load(f)
        for i, game in enumerate(data.copy()):
            if files[index] == final and i >= final_file_check_limit:
                break
            if current_timestamp - game["stop_time"] > days_to_seconds(30):
                if not found_expired:
                    found_expired = True
                data.remove(game)

        if found_expired:
            for file in files[:index]:
                with suppress(FileNotFoundError):
                    os.remove(file)
            if data:
                # Current file only partially expired.
                with gzip.open(files[index], "wt", encoding="utf8") as f:
                    json.dump(data, f, separators=(",", ":"))
                # Can now just continue - all expired files removed.
                files = files[index:]
                break
            with suppress(FileNotFoundError):
                os.remove(files[index])
            # Restart the process with files containing newer games only.
            files = files[index + 1:]
            index = len(files) // 2
            found_expired = False
        else:
            if not index or not files:
                break
            index //= 2
    return files


@check_folder_exists(GAME_DATA_FOLDER)
def get_game_data() -> list[dict]:
    """
    Gets data for all game rounds played in the past.
    """
    try:
        files = [
            f"{GAME_DATA_FOLDER}/{file}"
            for file in sorted(os.listdir(GAME_DATA_FOLDER), key=int)]
        if not files:
            return []

        # If maximum number of game data with n files is greater
        # than the max game data count, check to remove expired data.
        if len(files) * MAX_GAME_DATA_PER_FILE > MAX_ALLOWED_GAME_DATA:
            with gzip.open(files[-1], "rt", encoding="utf8") as f:
                last_file_game_data_count = len(json.load(f))

            # Number of ending files guaranteed to be allowed to stay.
            allowed_file_count = (
                (MAX_ALLOWED_GAME_DATA - last_file_game_data_count)
                // MAX_GAME_DATA_PER_FILE) + 1
            allowed_files = files[-allowed_file_count:]

            files = remove_expired_games(
                files[:-allowed_file_count],
                last_file_game_data_count) + allowed_files

        game_data = []
        for file in files:
            with gzip.open(file, "rt", encoding="utf8") as f:
                game_data.extend(json.load(f))
        return game_data
    except Exception:
        # Corruption has occurred. Delete all game data...
        # Most likely due to the program files being tampered with.
        shutil.rmtree(GAME_DATA_FOLDER)
        return []


@check_folder_exists(GAME_DATA_FOLDER)
def add_game_data(new_data: dict) -> None:
    """
    Adds game data.
    """
    # Newest file has largest number (-1 if empty).
    newest = int(max(os.listdir(GAME_DATA_FOLDER) or [-1], key=int))
    try:
        if newest != -1:
            file = f"{GAME_DATA_FOLDER}/{newest}"
            with gzip.open(file, "rt", encoding="utf8") as f:
                data = json.load(f)
            if len(data) < MAX_GAME_DATA_PER_FILE:
                data.append(new_data)
                with gzip.open(file, "wt", encoding="utf8") as f:
                    json.dump(data, f, separators=(",", ":"))
                return
        new_file = f"{GAME_DATA_FOLDER}/{newest + 1}"
        with gzip.open(new_file, "wt", encoding="utf8") as f:
            json.dump([new_data], f, separators=(",", ":"))
    except Exception:
        # Corruption
        shutil.rmtree(GAME_DATA_FOLDER)


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
        self.recent_games = get_game_data()[-MAX_ALLOWED_GAME_DATA:]

        self.title_label = tk.Label(
            self, font=ink_free(50, True), text="History")
        self.back_button = tk.Button(
            self, font=ink_free(15), text="Back", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=self.back)

        if self.recent_games:
            self.solutions_frame = None
            self.recent_game_frame = None
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
        # Index -1 of the list of recent games indicates the most recent.
        # (index 0 of the listbox).
        current_game = self.recent_games[-current_index-1]
        if self.recent_game_frame is not None:
            self.recent_game_frame.destroy()
        if self.solutions_frame is not None:
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
        Returns to the main history screen upon
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
        self.recent_game_frame = None
        self.solutions_frame = None

    def back(self) -> None:
        """
        Returns to the main menu.
        """
        self.destroy()
        if self.solutions_frame is not None:
            self.solutions_frame.destroy()
        menu.MainMenu(self.root).pack()


class RecentGamesFrame(tk.Frame):
    """
    Holds a listbox of recent games which can be
    vertically navigated with a scrollbar.
    """

    def __init__(self, master: HistoryWindow) -> None:
        super().__init__(master)
        self.listbox = tk.Listbox(
            self, font=ink_free(12), width=55, height=5, bg=GREEN, border=5)
        self.listbox.bind("<<ListboxSelect>>", lambda _: master.select_game())
        self.scrollbar = tk.Scrollbar(self, orient="vertical")

        for recent_game in master.recent_games:
            display = "{} | {} -> {} | {}".format(
                epoch_to_strftime(recent_game["start_time"]),
                str(tuple(recent_game["numbers"])), recent_game["target"],
                "✔️" if recent_game["is_win"] else "❌")
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
        self.listbox.insert("end", *xp_sources)
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
