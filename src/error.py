"""
Handles unhandled exceptions in the code.
"""
import tkinter as tk
import secrets
import sys
import traceback

import main
import data
from colours import *
from utils import ink_free, get_sfx


ERROR_SFX = [get_sfx(f"error{n}.wav") for n in range(1, 3)]


def tkinter_error(
    root: tk.Tk, exception: Exception, description: str, tback) -> None:
    """
    Catches any error and redirects player to the error window.
    """
    traceback.print_tb(tback)
    print(f"{exception.__name__}: {description}")
    root.protocol("WM_DELETE_WINDOW", lambda: "")
    root.destroy()
    unhandled_error()


def retry(old_root: tk.Tk) -> None:
    """
    Retries launching the main application.
    """
    old_root.destroy()
    main.main()


def existing_instance() -> None:
    """
    The window displayed if an instance of the application
    already exists.
    """
    root = tk.Tk()
    root.title("Application Instance Error")
    root.tk_setPalette(background=DEFAULT_BACKGROUND, foreground=BLACK)
    if data.get_options()["sfx"]:
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


def unhandled_error() -> None:
    """
    The window displayed if an unhandled error occurs in the program.
    """
    root = tk.Tk()
    root.title("Application Error")
    root.tk_setPalette(background=DEFAULT_BACKGROUND, foreground=BLACK)
    if data.get_options()["sfx"]:
        secrets.choice(ERROR_SFX).play()

    title_label = tk.Label(
        root, font=ink_free(75, True), text="Error", fg=RED)
    message_label = tk.Label(
        root, font=ink_free(25),
        text=("An unexpected error has occurred in the program.\n"
              "Sorry for the inconvenience."))
    exit_button = tk.Button(
        root, font=ink_free(25), text="Exit", width=20, border=5,
        bg=ORANGE, activebackground=RED, command=sys.exit)

    title_label.pack(padx=25, pady=25)
    message_label.pack(padx=25, pady=25)
    exit_button.pack(padx=25, pady=10)
    root.mainloop()