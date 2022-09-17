import tkinter as tk
import secrets

import menu
import game
import data
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
        self, root: tk.Tk, solution: str | None, target: int) -> None:

        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Finish")
        self.solution = solution
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
        
        self.options_frame = GameEndOptionsFrame(self, is_win)

        self.title_label.pack(padx=15, pady=10)
        self.message_label.pack(padx=10, pady=10)
        self.streak_label.pack(padx=10, pady=10)
        self.options_frame.pack(padx=10, pady=10)
    
    def play_again(self) -> None:
        """
        Allows the player to start another round.
        """
        self.destroy()
        game.Game(self.root).pack()
    
    def home(self) -> None:
        """
        Return to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()


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
            width=15, border=3, bg=ORANGE, activebackground=GREEN)
        self.play_again_button = tk.Button(
            self, font=ink_free(25), text="Play again", width=15, border=3,
            bg=ORANGE, activebackground=GREEN, command=master.play_again)
        self.home_button = tk.Button(
            self, font=ink_free(25), text="Home", width=15, border=3,
            bg=ORANGE, activebackground=GREEN, command=master.home)
        
        self.solutions_button.pack(padx=10, pady=5)
        self.play_again_button.pack(padx=10, pady=5)
        self.home_button.pack(padx=10, pady=5)