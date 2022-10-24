"""
Achievements serve as motivation for the player to
replay the game, adding engagement.
"""
import tkinter as tk

import menu
from colours import *
from utils import ink_free


class AchievementsWindow(tk.Frame):
    """
    Holds the achievements user interface.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Achievements")

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Achievements")
        
        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=self.back)
        
        self.title_label.pack(padx=10, pady=10)
        self.back_button.pack(padx=10, pady=10)
    
    def back(self) -> None:
        """
        Returns back to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()