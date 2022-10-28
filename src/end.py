"""
Module containing post-game functionality.
"""
import tkinter as tk
import secrets

import menu
import game
import data
import level
import solutions
import stats
from colours import *
from utils import get_sfx, ink_free, days_to_seconds
from achievements import (
    format_achievement, format_special_achievement, get_achievement_count)


OPERATORS = "+-x÷"

WINNING_MESSAGES = (
    "Amazing!", "Awesome!", "Brilliant!", "Congratulations!", "Excellent!",
    "Fabulous!", "Fantastic!", "Great work!", "Incredible!", "Keep it up!",
    "Magnificent!", "Outstanding!", "Perfect!", "Quintessential!",
    "Really, really good!", "Super!", "Terrific!", "Unbeatable!",
    "Well Done!", "WOW!")

LOSING_MESSAGES = (
    "Excellent effort!", "Good try!", "Hard number!", "I believe in you!",
    "Light is at the end of the tunnel!", "Maybe next time!",
    "Never give up!", "Oh well!", "Try again!", "Welp!")

XP_PER_OPERATOR = {
    "+": 5,
    "-": 6,
    "x": 8,
    "÷": 10
}

NUMBERS_USED_XP_MULTIPLIER = {
    5: 1.1,
    6: 1.2,
    7: 1.3
}

STREAK_XP_MULTIPLIER = {
    2: 1.1,
    5: 1.15,
    10: 1.2,
    15: 1.25,
    20: 1.3,
    25: 1.35,
    50: 1.5
}

ADD_XP_CHUNK_COUNT = 50
ADD_XP_DELAY_MS = 40

LEVEL_UP_SFX = get_sfx("levelup.wav")


def get_winning_message(solution: str, target: int) -> str:
    """
    Gets winning message with a random positive message
    followed by the player solution below.
    """
    return f"{secrets.choice(WINNING_MESSAGES)}\n{solution} = {target} ✓"


def get_losing_message() -> str:
    """
    Selects a random positive message despite the loss.
    """
    return secrets.choice(LOSING_MESSAGES)


def get_xp_earned(solution: str | None) -> tuple[int, list[str]]:
    """
    Gets the XP earned along with the sources of XP.
    """
    streak = data.get_win_streak()
    xp_earned = 25 # Just for playing
    xp_sources = ["Completed a round (+25XP)"]
    if solution is not None:
        xp_earned += 100 # Solution XP
        xp_sources.append("Solution (+100XP)")
        # Add operator XP
        for operator, xp in XP_PER_OPERATOR.items():
            count = solution.count(operator)
            if count:
                earned = count * xp
                xp_earned += earned
                xp_sources.append(
                    "{} operator x{} (+{}XP)".format(
                        operator, count, earned))
        
        if all(operator in solution for operator in "+-x÷"):
            # Bonus for using all operators.
            xp_earned += 50
            xp_sources.append("All operators used (+50XP)")

        numbers_used = 0
        currently_in_number = False
        for char in solution:
            if char.isdigit():
                if not currently_in_number:
                    numbers_used += 1
                    currently_in_number = True
            else:
                currently_in_number = False

        numbers_used_multiplier = NUMBERS_USED_XP_MULTIPLIER.get(numbers_used)
        if numbers_used_multiplier is not None:
            # Multiply XP by a factor if 5 or more numbers used.
            xp_earned *= numbers_used_multiplier
            xp_sources.append(
                "{} numbers used (x{})".format(
                    numbers_used, numbers_used_multiplier))

        # Apply Streak XP multiplier. Only apply the biggest one.
        for required_streak, multiplier in sorted(
            STREAK_XP_MULTIPLIER.items(),
            key=lambda streak_to_multiplier: streak_to_multiplier[0],
            reverse=True
        ):
            if streak >= required_streak:
                xp_earned *= multiplier
                xp_sources.append(
                    "Win streak {} or above (x{})".format(
                        required_streak, multiplier))
                break
        
        xp_earned = int(round(xp_earned, 10))
    
    return xp_earned, xp_sources


def get_achievements_earned(
    game_data: "GameData") -> list[str]:
    """
    Checks for any achievements earned and returns them.
    """
    earned = []
    games = data.get_game_data()
    starting_achievement_count = get_achievement_count()

    games_played_last_24_hours = len(
        stats.filter_by_time(games, days_to_seconds(1)))
    if games_played_last_24_hours >= 40:
        if data.complete_special_achievement("obsession"):
            earned.append(format_special_achievement("obsession"))

    games_played_last_7_days = len(
        stats.filter_by_time(games, days_to_seconds(7)))
    if games_played_last_7_days >= 250:
        if data.complete_special_achievement("addiction"):
            earned.append(format_special_achievement("addiction"))
    
    if game_data.small_numbers == 5 and game_data.big_numbers == 0:
        if data.complete_special_achievement("small_numbers"):
            earned.append(format_special_achievement("small_numbers"))
    elif game_data.big_numbers == 5 and game_data.small_numbers == 0:
        if data.complete_special_achievement("big_numbers"):
            earned.append(format_special_achievement("big_numbers"))
    elif game_data.big_numbers + game_data.small_numbers == 7:
        if data.complete_special_achievement("all_numbers"):
            earned.append(format_special_achievement("all_numbers"))
    
    if min(game_data.operator_counts.values()) > 0:
        # All operators used.
        if data.complete_special_achievement("all_operators"):
            earned.append(format_special_achievement("all_operators"))
    elif tuple(game_data.operator_counts.values()).count(0) == 3:
        # Only one operator used.
        if data.complete_special_achievement("one_operator"):
            earned.append(format_special_achievement("one_operator"))


    
    return earned


class GameData:
    """
    Holds data for a particular round, including stats and date/time.
    """

    def __init__(
        self, numbers: list[int], target: int, solution: str | None,
        start_time: float, stop_time: float
    ) -> None:
        self.numbers = numbers
        self.target = target
        self.solution = solution
        self.start_time = start_time
        self.stop_time = stop_time
        self.is_win = self.solution is not None
        self.big_numbers = 0
        self.small_numbers = 0

        if self.is_win:
            self.operator_counts = {
                operator: self.solution.count(operator)
                for operator in OPERATORS}

            number = ""
            # Space purposely added for final check for a number.
            for char in self.solution + " ":
                if char.isdigit():
                    number += char
                else:
                    if number:
                        if len(number) == 1:
                            self.small_numbers += 1
                        else:
                            self.big_numbers += 1
                        number = ""
        else:
            self.operator_counts = {operator: 0 for operator in OPERATORS}

        self.xp_earned, self.xp_sources = get_xp_earned(self.solution)
    
    def save(self) -> None:
        """
        Saves game data.
        """
        data.add_game_data(self.__dict__)


class GameEnd(tk.Frame):
    """
    Handles the post-game functionality after a solution is entered
    (or skipped). This includes:
    - Indicating a win or loss.
    - Displaying XP earned. If level up, display it.
    - Displaying any achievements earned that round.
    - Allowing the player to generate possible solutions.
    """

    def __init__(
        self, root: tk.Tk, solution: str | None, numbers: list[int],
        target: int, start_time: float, stop_time: float) -> None:

        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Finish")

        data.increment_games_played()

        old_streak = data.get_win_streak()
        if solution is not None:
            data.increment_win_streak()
        else:
            data.reset_win_streak()
        new_streak = data.get_win_streak()
        if new_streak > data.get_best_win_streak():
            data.increment_best_win_streak()

        self.game_data = GameData(
            numbers, target, solution, start_time, stop_time)
        self.game_data.save()
        if self.game_data.is_win:
            data.increment_win_count()
            if self.game_data.small_numbers:
                data.add_small_numbers_used(self.game_data.small_numbers)
            if self.game_data.big_numbers:
                data.add_big_numbers_used(self.game_data.big_numbers)
        data.add_seconds_played(stop_time - start_time)
        data.add_operators_used(self.game_data.operator_counts)

        level_before = level.Level().level
        total_xp_before = data.get_total_xp()
        self.new_total_xp = total_xp_before + self.game_data.xp_earned

        achievements_earned = get_achievements_earned(self.game_data)

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Finish")
        
        message = (
            get_winning_message(
                self.game_data.solution, self.game_data.target)
            if self.game_data.is_win else get_losing_message())
        self.message_label = tk.Label(
            self, font=ink_free(25, italic=True), text=message, width=60)

        self.streak_label = tk.Label(
            self, font=ink_free(25), text="Streak: {} -> {}".format(
                old_streak, new_streak
            ))

        self.xp_frame = GameEndXpFrame(
            self, self.game_data.xp_sources,
            self.game_data.xp_earned, level_before)
        
        self.options_frame = GameEndOptionsFrame(self, self.game_data.is_win)

        self.solutions_frame = solutions.SolutionsFrame(
            self.root, self, self.game_data.numbers, self.game_data.target)

        self.title_label.pack(padx=15, pady=5)
        self.message_label.pack(padx=10, pady=5)
        self.streak_label.pack(padx=10, pady=5)
        self.xp_frame.pack(padx=10, pady=5)
        self.options_frame.pack(padx=10, pady=10)
    
    def exit(self) -> None:
        """
        Exits the game over screen.
        """
        LEVEL_UP_SFX.stop()
        self.destroy()
        self.solutions_frame.destroy()
        # In case animated XP gain is not finished.
        current_total_xp = data.get_total_xp()
        if current_total_xp < self.new_total_xp:
            data.add_total_xp(self.new_total_xp - current_total_xp)
    
    def play_again(self) -> None:
        """
        Allows the player to start another round.
        """
        self.exit()
        game.Game(self.root).pack()
    
    def home(self) -> None:
        """
        Return to the main menu.
        """
        self.exit()
        menu.MainMenu(self.root).pack()
    
    def solutions(self) -> None:
        """
        Allows the player to generate solutions.
        """
        self.pack_forget()
        self.solutions_frame.pack()
        self.root.title("Countdown - Finish - Solutions")
    
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
        self.root.title("Countdown - Finish")
        self.pack()
    

class GameEndXpFrame(tk.Frame):
    """
    Displays the XP earned by the player in the round, and how.
    Also displays the new level progress and if the player levelled
    up this round, this is indicated.
    """

    def __init__(
        self, master: GameEnd, sources: list[str], earned: int,
        level_before: int) -> None:

        super().__init__(master)
        self.level_before = level_before
        self.title = tk.Label(self, font=ink_free(25, True), text="XP/Level")

        self.xp_sources_listbox = tk.Listbox(
            self, font=ink_free(15), width=25, height=5)
        for source in sources:
            self.xp_sources_listbox.insert("end", source)
        
        self.earned_label = tk.Label(
            self, font=ink_free(20), text=f"Total: {earned}XP")

        self.level_data_frame = level.LevelLabelFrame(self, level.Level())
        
        self.title.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.xp_sources_listbox.grid(row=1, column=0, padx=5)
        self.earned_label.grid(row=2, column=0, padx=5)
        self.level_data_frame.grid(row=1, column=1, padx=5)

        self.add_xp_in_chunks(earned, ADD_XP_CHUNK_COUNT)
    
    def add_xp_in_chunks(
        self, xp_remaining: int, chunks_remaining: int) -> None:
        """
        Animates XP gain by adding it over a set period of time
        rather than instantly.
        """
        if not xp_remaining:
            final = level.Level()
            if final.level > self.level_before:
                LEVEL_UP_SFX.play()
                self.level_change_label = tk.Label(
                    self, font=ink_free(20),
                    text="Level Up! ({} -> {})".format(
                        self.level_before, final.level
                    ), fg=GREEN)
            else:
                self.level_change_label = tk.Label(
                    self, font=ink_free(20), text="No change")
            self.level_change_label.grid(row=2, column=1, padx=5)
            return

        xp_to_add = xp_remaining // chunks_remaining
        if xp_to_add:
            data.add_total_xp(xp_to_add)
            self.level_data_frame.update(level.Level())

        self.after(ADD_XP_DELAY_MS, lambda: self.add_xp_in_chunks(
            xp_remaining - xp_to_add, chunks_remaining - 1))


class GameEndOptionsFrame(tk.Frame):
    """
    Holds buttons which allow the player to either:
    - Find solutions
    - Play again
    - Return to the main menu
    """

    def __init__(self, master: GameEnd, is_win: bool) -> None:
        super().__init__(master)

        self.solutions_button = tk.Button(
            self, font=ink_free(25), text=(
                "Other solutions" if is_win else "Solutions"),
            width=15, border=3, bg=ORANGE, activebackground=GREEN,
            command=master.solutions)
        self.play_again_button = tk.Button(
            self, font=ink_free(25), text="Play again", width=15, border=3,
            bg=ORANGE, activebackground=GREEN, command=master.play_again)
        self.home_button = tk.Button(
            self, font=ink_free(25), text="Home", width=15, border=3,
            bg=ORANGE, activebackground=GREEN, command=master.home)
        
        self.solutions_button.pack(padx=10, side="left")
        self.play_again_button.pack(padx=10, side="left")
        self.home_button.pack(padx=10, side="right")