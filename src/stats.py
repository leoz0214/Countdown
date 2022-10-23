"""
Displays statistics of gameplay to the player.
"""
import tkinter as tk
import time

import menu
import data
import level
from colours import *
from utils import days_to_seconds, seconds_to_hhmmss, bool_to_state, ink_free


OPERATORS = "+-x÷"
TIME_CATEGORIES = ("Last 24 hours", "Last 7 days", "Last 30 days", "All time")


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
    data = {
        "games_played": len(games),
        "wins": 0,
        "seconds_played": 0,
        "operators_used": {operator: 0 for operator in OPERATORS},
        "big_numbers": 0,
        "small_numbers": 0,
        "xp_earned": 0
    }
    current_time = time.time()
    for i, game in enumerate(games):
        if game["is_win"]:
            data["wins"] += 1

        if i == 0 and game["start_time"] < current_time - seconds:
            # Oldest game only includes the time it is within the
            # maximum time in the past.
            # E.g a game was played from t = 0s to t = 100s
            # Current t = 150s
            # Within the last 100s, the game was played for only 50s.
            data["seconds_played"] += (
                game["stop_time"] - (current_time - seconds))
        else:
            data["seconds_played"] += (game["stop_time"] - game["start_time"])

        for operator, count in game["operator_counts"].items():
            data["operators_used"][operator] += count
        
        data["big_numbers"] += game["big_numbers"]
        data["small_numbers"] += game["small_numbers"]
        data["xp_earned"] += game["xp_earned"]
    
    return data
        

class StatisticsWindow(tk.Frame):
    """
    Allows the player to view statistics of their gameplay.
    """

    def __init__(self, root: tk.Tk, page_number: int = 1) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Statistics")

        last_30_days = data.get_game_data()
        if len(last_30_days) <= data.MAX_ALLOWED_GAME_DATA:
            # Possiblly over 30 days old.
            last_30_days = filter_by_time(last_30_days, days_to_seconds(30))
        
        last_7_days = filter_by_time(last_30_days, days_to_seconds(7))
        last_24_hours = filter_by_time(last_7_days, days_to_seconds(1))

        last_24_hours_data = get_all_stats(last_24_hours, days_to_seconds(1))
        last_7_days_data = get_all_stats(last_7_days, days_to_seconds(7))
        last_30_days_data = get_all_stats(last_30_days, days_to_seconds(30))

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Statistics")

        self.pages_frame = PagesFrame(
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
        self.refresh_button.grid(
            row=2, column=1, padx=10, pady=10, sticky="w")
    
    def back(self) -> None:
        """
        Returns back to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()
    
    def refresh(self) -> None:
        """
        Refresh statistics (time changes).
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
        self.parts = [
            (
                tk.Label(
                    self, font=ink_free(15),
                    text=f"{category}:", width=15, anchor="e"),
                tk.Label(
                    self, font=ink_free(15),
                    text=value, width=statistic_width, anchor="e")
            )
            for value, category in zip(values, TIME_CATEGORIES)]
        
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

        operator_headings = [
            tk.Label(
                self, font=ink_free(15, True), width=3,
                text=operator, anchor="e") for operator in OPERATORS]
        
        values = (last_24_hours, last_7_days, last_30_days, all_time)
        self.parts = [
            [
                tk.Label(
                    self, font=ink_free(12),
                    text=f"{category}:", width=15, anchor="e")] +
            [
                tk.Label(
                    self, font=ink_free(10), text=count, anchor="e", width=8)
                for count in value.values()]
            for value, category in zip(values, TIME_CATEGORIES)]
        
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


class PagesFrame(tk.Frame):
    """
    Allows stats to be placed into pages, which can be cycled
    through.
    """

    def __init__(
        self, master: StatisticsWindow, starting_page_number: int,
        last_24_hours_data: dict, last_7_days_data: dict,
        last_30_days_data: dict
    ) -> None:
        super().__init__(master, width=1200, height=360)
        # Keep size of frame constant as the current page changes.
        self.pack_propagate(False)
        self.pages = []

        first_page = tk.Frame(self)
        games_played_frame = TimedStatisticLabelFrame(
            first_page, "Games played", 10,
            last_24_hours_data["games_played"],
            last_7_days_data["games_played"],
            last_30_days_data["games_played"], data.get_games_played())
        
        games_won_frame = TimedStatisticLabelFrame(
            first_page, "Games won", 10,
            last_24_hours_data["wins"], last_7_days_data["wins"],
            last_30_days_data["wins"], data.get_win_count())
        
        time_played_frame = TimedStatisticLabelFrame(
            first_page, "Time played (HH:MM:SS)", 10,
            seconds_to_hhmmss(last_24_hours_data["seconds_played"]),
            seconds_to_hhmmss(last_7_days_data["seconds_played"]),
            seconds_to_hhmmss(last_30_days_data["seconds_played"]),
            seconds_to_hhmmss(data.get_seconds_played()))

        games_played_frame.pack(side="left", padx=10, pady=10)
        games_won_frame.pack(side="left", padx=10, pady=10)
        time_played_frame.pack(padx=10, pady=10)
        self.pages.append(first_page)

        second_page = tk.Frame(self)
        operators_used_frame = OperatorsUsedLabelFrame(
            second_page, last_24_hours_data["operators_used"],
            last_7_days_data["operators_used"],
            last_30_days_data["operators_used"], data.get_operators_used())

        small_numbers_used_frame = TimedStatisticLabelFrame(
            second_page, "Small numbers used", 10,
            last_24_hours_data["small_numbers"],
            last_7_days_data["small_numbers"],
            last_30_days_data["small_numbers"], data.get_small_numbers_used())

        big_numbers_used_frame = TimedStatisticLabelFrame(
            second_page, "Big numbers used", 10,
            last_24_hours_data["big_numbers"],
            last_7_days_data["big_numbers"],
            last_30_days_data["big_numbers"], data.get_big_numbers_used())
        
        operators_used_frame.pack(side="left", padx=10, pady=10)
        small_numbers_used_frame.pack(side="left", padx=10, pady=10)
        big_numbers_used_frame.pack(padx=10, pady=10)
        self.pages.append(second_page)
    
        third_page = tk.Frame(self)
        xp_earned_frame = TimedStatisticLabelFrame(
            third_page, "XP earned", 10,
            last_24_hours_data["xp_earned"], last_7_days_data["xp_earned"],
            last_30_days_data["xp_earned"], data.get_total_xp())

        level_frame = level.LevelLabelFrame(third_page, level.Level())

        best_win_streak_frame = BestWinStreakLabelFrame(
            third_page, data.get_best_win_streak())

        xp_earned_frame.pack(side="left", padx=10, pady=10)
        level_frame.pack(side="left", anchor="n", padx=10, pady=10)
        best_win_streak_frame.pack(padx=10, pady=10)
        self.pages.append(third_page)

        self.first_page = 1
        self.last_page = self.total_pages = len(self.pages)
        self.current_page = starting_page_number

        self.navigation_frame = PageNavigationFrame(self)
        self.navigation_frame.pack(padx=10, pady=10)

        self.pages[self.current_page - 1].pack(padx=10, pady=10)


class PageNavigationFrame(tk.Frame):
    """
    Allows the page number to be changed.
    """

    def __init__(self, master: PagesFrame) -> None:
        super().__init__(master)
        self.master = master
        self.back_button = tk.Button(
            self, font=ink_free(25), text="<", width=3, border=5,
            bg=ORANGE, activebackground=GREEN,
            state=bool_to_state(
                self.master.current_page != self.master.first_page),
            command=self.back)
        self.current_page_label = tk.Label(
            self, font=ink_free(25),
            text=f"{self.master.current_page} / {self.master.total_pages}",
            width=8)
        self.forward_button = tk.Button(
            self, font=ink_free(25), text=">", width=3, border=5,
            bg=ORANGE, activebackground=GREEN,
            state=bool_to_state(
                self.master.current_page != self.master.last_page),
            command=self.forward)
        
        self.back_button.pack(side="left")
        self.current_page_label.pack(side="left")
        self.forward_button.pack()
    
    def back(self) -> None:
        """
        Move back a page.
        """
        self.master.pages[self.master.current_page - 1].pack_forget()
        self.master.current_page -= 1
        self.current_page_label.config(
            text=f"{self.master.current_page} / {self.master.total_pages}")
        if self.master.current_page == self.master.first_page:
            self.back_button.config(state="disabled")
        # Can definitely go forward.
        self.forward_button.config(state="normal")
        self.master.pages[self.master.current_page - 1].pack(padx=10, pady=10)
    
    def forward(self) -> None:
        """
        Move forward a page.
        """
        self.master.pages[self.master.current_page - 1].pack_forget()
        self.master.current_page += 1
        self.current_page_label.config(
            text=f"{self.master.current_page} / {self.master.total_pages}")
        if self.master.current_page == self.master.last_page:
            self.forward_button.config(state="disabled")
        # Can definitely go back.
        self.back_button.config(state="normal")
        self.master.pages[self.master.current_page - 1].pack(padx=10, pady=10)