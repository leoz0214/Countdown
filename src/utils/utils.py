"""
Utility functions for the rest of the application.
"""
import datetime
import tkinter as tk
from ctypes import cdll, c_double, CDLL

from pygame import mixer


def load_cpp_library(filename: str) -> CDLL:
    """
    Loads a C++ library in the bin folder with a particular filename.
    Path not required, just the name of the file.
    """
    return cdll.LoadLibrary(f"./bin/{filename}")


fast_eval = load_cpp_library("generate.so").eval
fast_eval.restype = c_double

mixer.init()

AUDIO_FOLDER = "./audio"
MUSIC_FOLDER = f"{AUDIO_FOLDER}/music"
SFX_FOLDER = f"{AUDIO_FOLDER}/sfx"


def ink_free(size: int, bold: bool = False, italic: bool = False) -> tuple:
    """
    Utility function for 'Ink Free' font.
    """
    font = ("Ink Free", size)
    if bold:
        font += ("bold",)
    if italic:
        font += ("italic",)
    return font


def evaluate(expression: str) -> int | float:
    """
    Evaluates a simple maths expression with only +/-/*/'/'/().
    Order of operations followed.
    Not for general purpose - meets the program requirements,
    and that's it. Safer and faster than the built-in eval.

    Calls fast corresponding function written in C++.
    """
    result = fast_eval(expression.encode(), 0, -1)
    if "/" in expression:
        result = round(result, 10)
        return int(result) if result.is_integer() else result
    return int(result)


def draw_circle(
    canvas: tk.Canvas, x: int, y: int, radius: int,
    fill: str | None = None, outline: str = "black") -> None:
    """
    Draws a circle with a given centre and radius onto the canvas.
    """
    canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius,
        fill=fill, outline=outline)


def days_to_seconds(days: int) -> int:
    """
    Converts days to seconds. 1 day = 86400 seconds
    """
    return days * 86400


def seconds_to_hhmmss(seconds: int | float) -> str:
    """
    Converts seconds to HH:MM:SS format.
    """
    seconds = int(seconds)

    hours = str(seconds // 3600).zfill(2)
    minutes = str((seconds % 3600) // 60).zfill(2)
    seconds = str(seconds % 60).zfill(2)

    return f"{hours}:{minutes}:{seconds}"


def human_expression(expression: str) -> str:
    """
    Converts an expression formatted for the program to
    process into the common equivalent people use in everyday life.
    Multiplication: * -> x
    Division: / -> ÷
    """
    return expression.replace("*", "x").replace("/", "÷")


def machine_expression(expression: str) -> str:
    """
    Converts an expression formatted for people to read into
    the equivalent which the program can use more effectively.
    Multiplication: x -> *
    Division: ÷ -> /
    """
    return expression.replace("x", "*").replace("÷", "/")


def bool_to_state(expression: bool) -> str:
    """
    Returns 'normal' if expression evaluates to True, else 'disabled'.
    Useful to control the state of a Tkinter widget based on the
    value of a Boolean.
    """
    return "normal" if expression else "disabled"


def epoch_to_strftime(epoch: float) -> str:
    """
    Converts seconds since epoch into the corresponding
    human readable time (system time zone).

    The ISO 8601 format YYYY-MM-DD is used for date,
    and time is in HH:MM:SS.
    """
    return datetime.datetime.fromtimestamp(epoch).strftime(
        "%Y-%m-%d %H:%M:%S")


def get_sfx(filename: str) -> mixer.Sound:
    """
    Gets the SFX with a particular filename, returning a Sound object.
    Path not required, just the name of the file.
    """
    return mixer.Sound(f"{SFX_FOLDER}/{filename}")


def get_music(filename: str) -> mixer.Sound:
    """
    Gets the music with a particular filename, returning a Sound object.
    Path not required, just the name of the file.
    """
    return mixer.Sound(f"{MUSIC_FOLDER}/{filename}")
