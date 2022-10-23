"""
The main module of the application.
This is the file that is run for the application to start.
"""
import tkinter as tk
from tkinter import messagebox
import sys
import secrets

from tendo import singleton

import menu
import game
import end
import data
from colours import *
from utils import get_sfx, ink_free


ERROR_SFX = [get_sfx(f"error{n}.wav") for n in range(1, 3)]


def main() -> None:
    """
    Main function of the program.
    """
    data.remove_temp_folder()
    # Only allows one instance of the main program to be run at any time.
    # Prevents the risks of race conditions, especially during IO.
    # Defensive.
    try:
        global instance_check # Required for check to work in function.
        instance_check = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        existing_instance()
    else:
        launch()


def launch() -> None:
    """
    Runs the main application.
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
                "Your stats will be unaffected, but "
                "this round will be counted as a loss. "
                "Your streak will be reset.", icon="warning"
        ):
            return
        data.reset_win_streak()
    elif isinstance(frame, end.GameEnd):
        frame.exit()

    sys.exit()


def retry(old_root: tk.Tk) -> None:
    """
    Retries launching the main application.
    """
    old_root.destroy()
    main()


def existing_instance() -> None:
    """
    The window displayed if an instance of the application
    already exists.
    """
    root = tk.Tk()
    root.title("Application Instance Error")
    root.tk_setPalette(background=DEFAULT_BACKGROUND, foreground=BLACK)
    secrets.choice(ERROR_SFX).play()

    title_label = tk.Label(
        root, font=ink_free(75, True), text="Error", fg=RED)
    message_label = tk.Label(
        root, font=ink_free(25),
        text=("An instance of the application is already running.\n"
              "Only one instance can be run at any time.\n"
              "Sorry for the inconvenience."))
    retry_button = tk.Button(
        root, font=ink_free(25), text="Retry", width=20, border=5,
        bg=ORANGE, activebackground=GREEN, command=lambda: retry(root))
    exit_button = tk.Button(
        root, font=ink_free(25), text="Exit", width=20, border=5,
        bg=ORANGE, activebackground=RED, command=sys.exit)

    title_label.pack(padx=25, pady=25)
    message_label.pack(padx=25, pady=25)
    retry_button.pack(padx=25, pady=10)
    exit_button.pack(padx=25, pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()