import tkinter as tk

from colours import *
from font import ink_free


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

        self.title_label = tk.Label(
            self, font=ink_free(100, True), text="Finish")

        self.title_label.pack(padx=15, pady=15)
