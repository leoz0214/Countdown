import tkinter as tk
from tkinter import messagebox
import sys

import menu
import game
import end
import data
from colours import *


def main() -> None:
    """
    Main function of app.
    """
    root = tk.Tk()
    root.tk_setPalette(background=DEFAULT_BACKGROUND, foreground=BLACK)
    root.protocol("WM_DELETE_WINDOW", lambda: close_window(root))
    main_menu = menu.MainMenu(root)
    main_menu.pack()
    root.mainloop()


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
    elif isinstance(frame, end.GameEnd):
        frame.exit()

    sys.exit()


if __name__ == "__main__":
    main()