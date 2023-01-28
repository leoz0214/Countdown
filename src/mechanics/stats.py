"""
Handles and displays statistics of gameplay to the player.
"""
import json
import time
import tkinter as tk
from typing import Callable

import menu
from utils import widgets
from utils.colours import *
from utils.io import FOLDER, check_folder_exists
from utils.utils import days_to_seconds, seconds_to_hhmmss, ink_free
from . import history
from . import level


OPERATORS = "+-x÷"
TIME_CATEGORIES = ("Last 24 hours", "Last 7 days", "Last 30 days", "All time")
PAGE_COUNT = 3

STATS_FOLDER = f"{FOLDER}/stats"
XP_FILE = f"{STATS_FOLDER}/xp.dat"
GAMES_PLAYED_FILE = f"{STATS_FOLDER}/played.dat"
GAMES_WON_FILE = f"{STATS_FOLDER}/won.dat"
BEST_WIN_STREAK_FILE = f"{STATS_FOLDER}/best_streak.dat"
SMALL_NUMBERS_FILE = f"{STATS_FOLDER}/small.dat"
BIG_NUMBERS_FILE = f"{STATS_FOLDER}/big.dat"
SECONDS_PLAYED_FILE = f"{STATS_FOLDER}/time.dat"
OPERATORS_USED_FILE = f"{STATS_FOLDER}/operators.json"

STREAK_FILE = f"{FOLDER}/streak.dat"



def get_incremental_data_functions(
    file: str, folder: str = FOLDER) -> tuple[Callable]:
    """
    Creates simple incremental data functions to be used for a variety
    of data that needs to be stored in this program.
    """
    @check_folder_exists(folder)
    def get() -> int:
        try:
            with open(file, "rb") as f:
                value = int(f.read())
            if value < 0:
                raise ValueError
            return value
        except (FileNotFoundError, ValueError):
            # File does not exist or is corrupt.
            with open(file, "wb") as f:
                f.write(b"0")
            return 0

    @check_folder_exists(folder)
    def increment() -> None:
        new = get() + 1
        with open(file, "wb") as f:
            f.write(str(new).encode())

    return get, increment


def get_additive_data_functions(
    file: str, folder: str = FOLDER, data_type: type = int) -> tuple[Callable]:
    """
    Creates simple additive data functions (for adding to a number).
    """
    @check_folder_exists(folder)
    def get() -> data_type:
        try:
            with open(file, "rb") as f:
                value = data_type(f.read())
            if value < 0:
                raise ValueError
            return value
        except (FileNotFoundError, ValueError):
            # File does not exist or is corrupt.
            with open(file, "wb") as f:
                f.write(b"0")
            return 0

    @check_folder_exists(folder)
    def add(value: data_type) -> None:
        new = get() + value
        with open(file, "wb") as f:
            f.write(str(new).encode())

    return get, add


get_win_streak, increment_win_streak = (
    get_incremental_data_functions(STREAK_FILE))

get_games_played, increment_games_played = (
    get_incremental_data_functions(GAMES_PLAYED_FILE, STATS_FOLDER))

get_win_count, increment_win_count = (
    get_incremental_data_functions(GAMES_WON_FILE, STATS_FOLDER))

get_best_win_streak, increment_best_win_streak = (
    get_incremental_data_functions(BEST_WIN_STREAK_FILE, STATS_FOLDER))

get_total_xp, add_total_xp = (
    get_additive_data_functions(XP_FILE, STATS_FOLDER))

get_small_numbers_used, add_small_numbers_used = (
    get_additive_data_functions(SMALL_NUMBERS_FILE, STATS_FOLDER))

get_big_numbers_used, add_big_numbers_used = (
    get_additive_data_functions(BIG_NUMBERS_FILE, STATS_FOLDER))

get_seconds_played, add_seconds_played = (
    get_additive_data_functions(SECONDS_PLAYED_FILE, STATS_FOLDER, float))


@check_folder_exists()
def reset_win_streak() -> None:
    """
    Resets win streak to 0
    """
    with open(STREAK_FILE, "wb") as f:
        f.write(b"0")


@check_folder_exists(STATS_FOLDER)
def get_operators_used() -> dict[str, int]:
    """
    Gets the number of times each operator has been used:
    addition, subtraction, multiplication and division.
    """
    try:
        with open(OPERATORS_USED_FILE, "r", encoding="utf8") as f:
            operators_used = json.load(f)
        if (
            not isinstance(operators_used, dict) or len(operators_used) != 4
            or "".join(operators_used) != OPERATORS or
            any(
                not isinstance(count, int) or count < 0
                for count in operators_used.values())
        ):
            raise ValueError
        return operators_used
    except (FileNotFoundError, ValueError):
        new = dict.fromkeys(OPERATORS, 0)
        with open(OPERATORS_USED_FILE, "w", encoding="utf8") as f:
            json.dump(new, f)
        return new


@check_folder_exists(STATS_FOLDER)
def add_operators_used(operators_used: dict[str, int]) -> None:
    """
    Adds operators used to the running totals.
    """
    new = get_operators_used()
    for operator, used in operators_used.items():
        new[operator] += used
    with open(OPERATORS_USED_FILE, "w", encoding="utf8") as f:
        json.dump(new, f)


def filter_by_time(games: list[dict], seconds: int) -> list[dict]:
    """
    Gets games which ended a certain length of time ago.
    Games are indeed in chronological order.
    Binary search for first valid game - O(log n) time complexity.
    """
    first = 0
    last = len(games) - 1
    current_time = time.time()
    while first <= last:
        midpoint = (first + last) // 2
        if current_time - games[midpoint]["stop_time"] <= seconds:
            if (
                midpoint == 0 or
                current_time - games[midpoint - 1]["stop_time"] > seconds
            ):
                return games[midpoint:]
            last = midpoint - 1
        else:
            first = midpoint + 1
    return games if last <= 0 and len(games) > 1 else []


def get_all_stats(games: list[dict], seconds: int) -> dict:
    """
    Returns a dictionary of totals for each category of game data.
    Maximum number of seconds in the past must be specified so that
    time played may only include part of the oldest game.
    """
    stats_data = {
        "games_played": len(games),
        "wins": 0,
        "seconds_played": 0,
        "operators_used": dict.fromkeys(OPERATORS, 0),
        "big_numbers": 0,
        "small_numbers": 0,
        "xp_earned": 0
    }
    current_time = time.time()
    for game in games:
        if game["is_win"]:
            stats_data["wins"] += 1
        if game["start_time"] < current_time - seconds:
            stats_data["seconds_played"] += (
                game["stop_time"] - (current_time - seconds))
        else:
            stats_data["seconds_played"] += (
                game["stop_time"] - game["start_time"])

        for operator, count in game["operator_counts"].items():
            stats_data["operators_used"][operator] += count

        stats_data["big_numbers"] += game["big_numbers"]
        stats_data["small_numbers"] += game["small_numbers"]
        stats_data["xp_earned"] += game["xp_earned"]
    return stats_data


class StatisticsWindow(tk.Frame):
    """
    Allows the player to view statistics of their gameplay.
    """

    def __init__(self, root: tk.Tk, page_number: int = 1) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Statistics")

        last_30_days = history.get_game_data()
        if len(last_30_days) <= history.MAX_ALLOWED_GAME_DATA:
            # Possibly over 30 days old.
            last_30_days = filter_by_time(last_30_days, days_to_seconds(30))
        last_7_days = filter_by_time(last_30_days, days_to_seconds(7))
        last_24_hours = filter_by_time(last_7_days, days_to_seconds(1))

        last_24_hours_data = get_all_stats(last_24_hours, days_to_seconds(1))
        last_7_days_data = get_all_stats(last_7_days, days_to_seconds(7))
        last_30_days_data = get_all_stats(last_30_days, days_to_seconds(30))

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Statistics")
        self.pages_frame = StatisticsPagesFrame(
            self, page_number,
            last_24_hours_data, last_7_days_data, last_30_days_data)
        self.back_button = tk.Button(
            self, font=ink_free(25), width=10, border=5, text="Back",
            bg=ORANGE, activebackground=RED, command=self.back)
        self.refresh_button = tk.Button(
            self, font=ink_free(25), width=10, border=5, text="Refresh",
            bg=ORANGE, activebackground=GREEN, command=self.refresh)

        self.title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.pages_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.back_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.refresh_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    def back(self) -> None:
        """
        Returns back to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()

    def refresh(self) -> None:
        """
        Refresh statistics to account for a change in time.
        """
        self.destroy()
        StatisticsWindow(self.root, self.pages_frame.current_page).pack()


class TimedStatisticLabelFrame(tk.LabelFrame):
    """
    Holds a statistic which can be viewed by time:
    - Last 24 hours
    - Last 7 days
    - Last 30 days
    - All time
    """

    def __init__(
        self, master: tk.Frame, title: str, statistic_width: int,
        last_24_hours: int | float, last_7_days: int | float,
        last_30_days: int | float, all_time: int | float
    ) -> None:
        super().__init__(
            master, text=title, font=ink_free(25, True),
            labelanchor="n", padx=10, pady=5)

        values = (last_24_hours, last_7_days, last_30_days, all_time)
        self.parts = (
            (
                tk.Label(
                    self, font=ink_free(15),
                    text=f"{category}:", width=15, anchor="e"),
                tk.Label(
                    self, font=ink_free(15),
                    text=value, width=statistic_width, anchor="e")
            )
            for value, category in zip(values, TIME_CATEGORIES))
        for row, (category, value) in enumerate(self.parts):
            category.grid(row=row, column=0, padx=5, pady=5)
            value.grid(row=row, column=1, padx=5, pady=5)


class OperatorsUsedLabelFrame(tk.LabelFrame):
    """
    Holds a table showing the number of each operator being
    used over time.
    """

    def __init__(
        self, master: tk.Frame,
        last_24_hours: dict[str, int], last_7_days: dict[str, int],
        last_30_days: dict[str, int], all_time: dict[str, int]
    ) -> None:
        super().__init__(
            master, font=ink_free(25, True),
            text="Operators used", labelanchor="n", padx=10, pady=5)

        operator_headings = (
            tk.Label(
                self, font=ink_free(15, True), width=3,
                text=operator, anchor="e") for operator in OPERATORS)

        values = (last_24_hours, last_7_days, last_30_days, all_time)
        self.parts = (
            [
                tk.Label(
                    self, font=ink_free(12),
                    text=f"{category}:", width=15, anchor="e")] +
            [
                tk.Label(
                    self, font=ink_free(10), text=count, anchor="e", width=8)
                for count in value.values()]
            for value, category in zip(values, TIME_CATEGORIES))

        for column, heading in enumerate(operator_headings, 1):
            heading.grid(row=0, column=column)
        for row, part in enumerate(self.parts, 1):
            for column, label in enumerate(part):
                if column == 0:
                    # Category
                    label.grid(row=row, column=column, padx=5, pady=5)
                else:
                    label.grid(row=row, column=column)


class BestWinStreakLabelFrame(tk.LabelFrame):
    """
    Displays the best win streak ever achieved by the player.
    """

    def __init__(self, master: tk.Frame, best_streak: int) -> None:
        super().__init__(
            master, font=ink_free(25, True),
            text="Best win streak", labelanchor="n", padx=10, pady=10)

        self.best_win_streak_label = tk.Label(
            self, font=ink_free(75), text=best_streak, width=6)
        self.best_win_streak_label.pack()


class StatisticsPagesFrame(widgets.PagesFrame):
    """
    Allows stats to be placed into pages, which can be cycled
    through. Cannot fit all statistics on one page.
    """

    def __init__(
        self, master: StatisticsWindow, starting_page_number: int,
        last_24_hours_data: dict, last_7_days_data: dict,
        last_30_days_data: dict
    ) -> None:
        super().__init__(
            master, starting_page_number, PAGE_COUNT, width=1200, height=360)
        first_page = tk.Frame(self)
        games_played_frame = TimedStatisticLabelFrame(
            first_page, "Games played", 10,
            last_24_hours_data["games_played"],
            last_7_days_data["games_played"],
            last_30_days_data["games_played"], get_games_played())

        games_won_frame = TimedStatisticLabelFrame(
            first_page, "Games won", 10,
            last_24_hours_data["wins"], last_7_days_data["wins"],
            last_30_days_data["wins"], get_win_count())

        time_played_frame = TimedStatisticLabelFrame(
            first_page, "Time played (HH:MM:SS)", 10,
            seconds_to_hhmmss(last_24_hours_data["seconds_played"]),
            seconds_to_hhmmss(last_7_days_data["seconds_played"]),
            seconds_to_hhmmss(last_30_days_data["seconds_played"]),
            seconds_to_hhmmss(get_seconds_played()))

        games_played_frame.pack(side="left", padx=10, pady=10)
        games_won_frame.pack(side="left", padx=10, pady=10)
        time_played_frame.pack(padx=10, pady=10)
        self.add(first_page)

        second_page = tk.Frame(self)
        operators_used_frame = OperatorsUsedLabelFrame(
            second_page, last_24_hours_data["operators_used"],
            last_7_days_data["operators_used"],
            last_30_days_data["operators_used"], get_operators_used())

        small_numbers_used_frame = TimedStatisticLabelFrame(
            second_page, "Small numbers used", 10,
            last_24_hours_data["small_numbers"],
            last_7_days_data["small_numbers"],
            last_30_days_data["small_numbers"], get_small_numbers_used())

        big_numbers_used_frame = TimedStatisticLabelFrame(
            second_page, "Big numbers used", 10,
            last_24_hours_data["big_numbers"],
            last_7_days_data["big_numbers"],
            last_30_days_data["big_numbers"], get_big_numbers_used())

        operators_used_frame.pack(side="left", padx=10, pady=10)
        small_numbers_used_frame.pack(side="left", padx=10, pady=10)
        big_numbers_used_frame.pack(padx=10, pady=10)
        self.add(second_page)

        third_page = tk.Frame(self)
        xp_earned_frame = TimedStatisticLabelFrame(
            third_page, "XP earned", 10,
            last_24_hours_data["xp_earned"], last_7_days_data["xp_earned"],
            last_30_days_data["xp_earned"], get_total_xp())

        level_frame = level.LevelLabelFrame(third_page, level.Level())

        best_win_streak_frame = BestWinStreakLabelFrame(
            third_page, get_best_win_streak())

        xp_earned_frame.pack(side="left", padx=10, pady=10)
        level_frame.pack(side="left", anchor="n", padx=10, pady=10)
        best_win_streak_frame.pack(padx=10, pady=10)
        self.add(third_page)

        self.show()
