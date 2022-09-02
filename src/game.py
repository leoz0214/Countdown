import tkinter as tk

from font import ink_free


class Game(tk.Frame):
    """
    Holds the actual countdown game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Game")

        self.select_numbers_frame = SelectNumbersFrame(self)
        self.select_numbers_frame.pack()


class SelectNumbersFrame(tk.Frame):
    """
    Allows the play to select numbers to be used, either:
    - Big (25, 50, 75, 100)
    - Small (1-9)

    Minimum one of each, total 7.
    """

    def __init__(self, master: Game) -> None:
        super().__init__(master)

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Select Numbers")
        
        self.title_label.pack(padx=10, pady=10)