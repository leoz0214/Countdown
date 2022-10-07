import tkinter as tk

from font import ink_free


class StatisticsWindow(tk.Frame):
    """
    Allows the player to view statistics of their gameplay.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Statistics")

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Statistics")
        
        self.title_label.pack(padx=10, pady=10)