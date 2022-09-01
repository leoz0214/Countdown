import tkinter as tk


def ink_free(size: int, bold: bool = False) -> tuple:
    return ("Ink Free", size, "bold") if bold else ("Ink Free", size)


class MainMenu(tk.Frame):
    """
    The main menu of the application.
    This is displayed when the player launches the game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Main Menu")

        self.title_label = tk.Label(self, font=ink_free(100), text="Countdown")
        self.title_label.pack(padx=25)
        LevelLabelFrame(self, 1, 0).pack(pady=10)


class LevelLabelFrame(tk.LabelFrame):
    """
    Information about the player's current level and XP.
    """

    def __init__(
        self, master: MainMenu, level: int, xp: int | None = None) -> None:

        super().__init__(
            master, font=ink_free(25), text=f"Level {level}", labelanchor="n")
        self.master = master

        if level < 100:
            self.progress_bar = LevelProgressBar(self, xp / level)
            self.progress_label = tk.Label(
                self, font=ink_free(15), text=f"{xp} / {level * 100}")
            
            self.progress_bar.pack()
            self.progress_label.pack()
        else:
            # Max Level (100)
            self.max_level_label = tk.Label(
                self, font=ink_free(20), text="Max Level!")        
            self.max_level_label.pack(padx=25, pady=25)
        

class LevelProgressBar(tk.Frame):
    """
    Visually shows how far the player is into a level.
    """

    def __init__(self, master: LevelLabelFrame, progress: float) -> None:
        super().__init__(master)
        self.master = master

        green_width = int(progress * 2)
        self.canvas = tk.Canvas(self.master, width=200, height=8)
        self.canvas.create_rectangle(0, 0, green_width, 8, fill="green")
        self.canvas.create_rectangle(green_width, 0, 200, 8, fill="grey")
        self.canvas.pack(padx=25, pady=25)