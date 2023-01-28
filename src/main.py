"""
The main module of the application.
This is the file that is run for the application to start.
"""
import sys
import tkinter as tk
from tkinter import messagebox

from tendo import singleton

import end
import error
import game
import menu
from mechanics.options import get_option
from mechanics.stats import reset_win_streak
from utils.colours import *
from utils.io import remove_temp_folder


ICON_IMAGE_FILE = "./images/icon.ico"


def main() -> None:
    """
    Main function of the program.
    """
    # In case the program terminated unexpectedly.
    remove_temp_folder()
    # Only allows one instance of the main program to be run at any time.
    # Prevents the risks of race conditions, especially during IO.
    try:
        global instance_check # Required for check to work in function.
        instance_check = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        error.existing_instance()
    else:
        launch()


def launch() -> None:
    """
    Runs the main application.
    """
    root = tk.Tk()
    root.iconbitmap(ICON_IMAGE_FILE)
    root.tk_setPalette(background=DEFAULT_BACKGROUND, foreground=BLACK)
    root.protocol("WM_DELETE_WINDOW", lambda: close_window(root))
    menu.MainMenu(root).pack()
    root.mainloop()


def close_window(root: tk.Tk) -> None:
    """
    Cleanup code which runs when the player attempts to close the window.
    """
    frame = tuple(root.children.values())[0]

    if (
        isinstance(frame, game.Game) and get_option("stats")
        and not isinstance(frame.frame, game.SelectNumbersFrame)
    ):
        if not messagebox.askyesnocancel(
            "Quit Game",
                "You are in the middle of a round.\n"
                "Are you sure you would like to quit now?\n"
                "Your stats will be unaffected, but "
                "this round will be counted as a loss. "
                "Your streak will be reset.", icon="warning"
        ):
            return
        reset_win_streak()
    elif isinstance(frame, end.GameEnd):
        frame.exit()

    remove_temp_folder()
    sys.exit()


if __name__ == "__main__":
    tk.Tk.report_callback_exception = error.tkinter_error
    main()
