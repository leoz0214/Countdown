"""
Supports level functionality.
"""
import tkinter as tk

import data
import widgets
from colours import *
from utils import ink_free


MAX_LEVEL = 100


def get_total_xp_for_level(level: int) -> int:
    """
    Returns the total amount of XP to reach a certain level.
    """
    return round(((level - 1) ** 2  + (level - 1)) / 2) * 100


class Level:
    """
    Holds the player's current level and the amount of XP
    earned through that level.
    """

    def __init__(self) -> None:
        remaining_xp = data.get_total_xp()
        self.level = 1
        self.required = 100

        while remaining_xp >= self.required and self.level < MAX_LEVEL:
            remaining_xp -= self.required
            self.level += 1
            self.required += 100

        self.xp = remaining_xp

    def add_xp(self, xp: int) -> None:
        """
        Adds XP, levelling up automatically if the player reaches the
        required XP for the current level.
        """
        self.xp += xp
        data.add_total_xp(xp)

        while self.xp >= self.required and self.level < MAX_LEVEL:
            self.xp -= self.required
            self.level += 1
            self.required += 100


class LevelLabelFrame(tk.LabelFrame):
    """
    Information about the player's current level and XP.
    """

    def __init__(self, master: tk.Frame, level_data: Level) -> None:
        super().__init__(
            master, font=ink_free(25),
            text=f"Level {level_data.level}", labelanchor="n")
        self.data = level_data

        if self.data.level < MAX_LEVEL:
            self.progress_bar = LevelProgressBar(
                self, self.data.xp / self.data.required)
            self.progress_label = tk.Label(
                self, font=ink_free(15), width=15,
                text=f"{self.data.xp} / {self.data.required} XP")

            self.progress_bar.pack()
            self.progress_label.pack()
        else:
            self.max_level_label = tk.Label(
                self, font=ink_free(20), text="Max Level!", fg=GREEN)
            self.max_level_label.pack(padx=25, pady=25)

    def update(self, new_level_data: Level) -> None:
        """
        Changes level display data to new level data.
        """
        if new_level_data.level > self.data.level:
            self.config(text=f"Level {new_level_data.level}")
        elif self.data.level == MAX_LEVEL:
            # No change
            self.data = new_level_data
            return

        self.data = new_level_data

        if self.data.level < MAX_LEVEL:
            self.progress_bar.update(self.data.xp / self.data.required)
            self.progress_label.config(
                text=f"{self.data.xp} / {self.data.required} XP")
        else:
            self.progress_bar.destroy()
            self.progress_label.destroy()
            self.max_level_label = tk.Label(
                self, font=ink_free(20), text="Max Level!", fg=GREEN)
            self.max_level_label.pack(padx=25, pady=25)


class LevelProgressBar(tk.Frame):
    """
    Visually shows how far the player is into a level.
    """

    def __init__(self, master: LevelLabelFrame, progress: float) -> None:
        super().__init__(master)
        self.create(progress)

    def create(self, progress: float) -> None:
        """
        Creates the progress bar.
        """
        self.canvas = widgets.ProgressBar(self, progress, 200, 8)
        self.canvas.pack(padx=25, pady=25)

    def update(self, new_progress: float) -> None:
        """
        Changes the amount of level progress displayed.
        """
        self.canvas.destroy()
        self.create(new_progress)
