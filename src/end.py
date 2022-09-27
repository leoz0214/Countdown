import tkinter as tk
import secrets

import menu
import game
import data
import level
import audio
from colours import *
from font import ink_free


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

LEVEL_UP_SFX = audio.get_sfx("levelup.wav")


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
        self, root: tk.Tk, solution: str | None,
        numbers: list[int], target: int) -> None:

        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Finish")
        self.solution = solution
        self.numbers = numbers
        self.target = target

        is_win = self.solution is not None

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Finish")
        
        message = (
            get_winning_message(self.solution, self.target)
            if is_win else get_losing_message())
        self.message_label = tk.Label(
            self, font=ink_free(25), text=message, width=60)

        old_streak = data.get_win_streak()
        if is_win:
            data.increment_win_streak()
        else:
            data.reset_win_streak()
        new_streak = data.get_win_streak()

        self.streak_label = tk.Label(
            self, font=ink_free(25), text="Streak: {} -> {}".format(
                old_streak, new_streak
            ))
                
        xp_earned = 25 # Just for playing
        xp_sources = ["Completed a round (+25XP)"]
        level_before = level.Level().level
        total_xp_before = data.get_total_xp()
        if is_win:
            xp_earned += 100 # Solution XP
            xp_sources.append("Solution (+100XP)")
            # Add operator XP
            for operator, xp in XP_PER_OPERATOR.items():
                count = self.solution.count(operator)
                if count:
                    earned = count * xp
                    xp_earned += earned
                    xp_sources.append(
                        "{} operator x{} (+{}XP)".format(
                            operator, count, earned
                        ))
            
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

            numbers_used_multiplier = NUMBERS_USED_XP_MULTIPLIER.get(
                numbers_used, 1)
            if numbers_used_multiplier != 1:
                # Multiply XP by a factor if 5 or more numbers used.
                xp_earned *= numbers_used_multiplier
                xp_sources.append(
                    "{} numbers used (x{})".format(
                        numbers_used, numbers_used_multiplier
                    ))
    
            # Apply Streak XP multiplier. Only apply the biggest one.
            for required_streak, multiplier in sorted(
                STREAK_XP_MULTIPLIER.items(),
                key=lambda streak_to_multiplier: streak_to_multiplier[0],
                reverse=True
            ):
                if new_streak >= required_streak:
                    xp_earned *= multiplier
                    xp_sources.append(
                        "Win streak {} or above (x{})".format(
                            required_streak, multiplier
                        ))
                    break
            
            xp_earned = int(round(xp_earned, 10))
        
        self.new_total_xp = total_xp_before + xp_earned

        self.xp_frame = GameEndXpFrame(
            self, xp_sources, xp_earned, level_before)
        
        self.options_frame = GameEndOptionsFrame(self, is_win)

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
        self.solutions_frame = SolutionsFrame(
            self.root, self, self.numbers, self.target)
        self.solutions_frame.pack()
    
    def exit_solutions(self) -> None:
        """
        Returns to the main game over screen upon
        leaving solution generation.
        """
        self.solutions_frame.destroy()
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


class SolutionsFrame(tk.Frame):
    """
    Holds the window which allows the player to get solutions
    for a particular target number using smaller numbers,
    with certain criteria which can be set.
    """

    def __init__(
        self, root: tk.Tk, game_end: GameEnd,
        numbers: list[int], target: int) -> None:

        super().__init__(root)
        self.root = root
        self.game_end = game_end
        self.numbers = numbers
        self.target = target
        self.root.title("Countdown - Finish - Solutions")

        self.title_label = tk.Label(
            self, font=ink_free(100), text="Solutions")
        self.selected_numbers_frame = game.SelectedNumbersFrame(
            self, self.numbers)
        self.target_number_label = game.TargetNumberLabel(self, self.target)
        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back", width=15, border=3,
            bg=ORANGE, activebackground=GREEN,
            command=self.game_end.exit_solutions)

        self.title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.selected_numbers_frame.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10)
        self.target_number_label.grid(
            row=2, column=0, padx=10, pady=10, sticky="w")
        self.back_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)