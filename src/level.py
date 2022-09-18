import tkinter as tk

import data
from font import ink_free
from colours import *


MAX_LEVEL = 100


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

    def __init__(
        self, master: tk.Frame, level_data: Level) -> None:

        super().__init__(
            master, font=ink_free(25),
            text=f"Level {level_data.level}", labelanchor="n")

        if level_data.level < MAX_LEVEL:
            self.progress_bar = LevelProgressBar(
                self, level_data.xp / level_data.required * 100)
            self.progress_label = tk.Label(
                self, font=ink_free(15),
                text=f"{level_data.xp} / {level_data.required} XP")
            
            self.progress_bar.pack()
            self.progress_label.pack()
        else:
            self.max_level_label = tk.Label(
                self, font=ink_free(20), text="Max Level!", fg=GREEN)        
            self.max_level_label.pack(padx=25, pady=25)
        

class LevelProgressBar(tk.Frame):
    """
    Visually shows how far the player is into a level.
    """

    def __init__(self, master: LevelLabelFrame, progress: float) -> None:
        super().__init__(master)

        green_width = int(progress * 2) # 1 width per 0.5% of progress.
        self.canvas = tk.Canvas(master, width=200, height=8)
        self.canvas.create_rectangle(0, 0, green_width, 8, fill=GREEN)
        self.canvas.create_rectangle(green_width, 0, 200, 8, fill=GREY)
        self.canvas.pack(padx=25, pady=25)