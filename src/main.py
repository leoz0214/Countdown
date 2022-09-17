import tkinter as tk
from tkinter import messagebox
import os

import menu
import game
import data
from colours import *


def main() -> None:
    """
    Main function of app.
    """
    check_for_required_folders()
    root = tk.Tk()
    root.tk_setPalette(background=DEFAULT_BACKGROUND, foreground=BLACK)
    root.protocol("WM_DELETE_WINDOW", lambda: close_window(root))
    main_menu = menu.MainMenu(root)
    main_menu.pack()
    root.mainloop()


def check_for_required_folders() -> None:
    """
    Ensures the required folders for the game to work exist.
    These folders are created at runtime.
    """
    if not os.path.isdir("./data"):
        os.mkdir("./data")


def close_window(root: tk.Tk) -> None:
    """
    Cleanup code which runs when the window is closed.
    """
    frame = tuple(root.children.values())[0]

    if (
        isinstance(frame, game.Game)
        and not isinstance(frame.frame, game.SelectNumbersFrame)
    ):
        if not messagebox.askyesnocancel(
            "Quit Game",
                "You are in the middle of a round.\n"
                "Are you sure you would like to quit now?\n"
                "This round will be counted as a loss.", icon="warning"
        ):
            return
        data.reset_win_streak()

    quit()


if __name__ == "__main__":
    main()