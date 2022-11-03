"""
The main module of the application.
This is the file that is run for the application to start.
"""
import tkinter as tk
from tkinter import messagebox
import sys

from tendo import singleton

import menu
import game
import end
import error
import data
from colours import *


def main() -> None:
    """
    Main function of the program.
    """
    # In case the program terminated unexpectedly.
    data.remove_temp_folder()
    # Only allows one instance of the main program to be run at any time.
    # Prevents the risks of race conditions, especially during IO.
    # Defensive.
    try:
        global instance_check # Required for check to work in function.
        instance_check = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        error.existing_instance()
    else:
        launch()
        data.remove_temp_folder()


def launch() -> None:
    """
    Runs the main application.
    """
    root = tk.Tk()
    root.iconbitmap("./images/icon.ico")
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
        isinstance(frame, game.Game) and data.get_options()["stats"]
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
        data.reset_win_streak()
    elif isinstance(frame, end.GameEnd):
        frame.exit()

    data.remove_temp_folder()
    sys.exit()


if __name__ == "__main__":
    tk.Tk.report_callback_exception = (
        lambda root, exception, description, traceback: error.tkinter_error(
            root, exception, description, traceback))
    main()