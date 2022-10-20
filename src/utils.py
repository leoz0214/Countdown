import tkinter as tk
import os
from ctypes import cdll, c_double


fast_eval = cdll.LoadLibrary(
    f"{os.path.dirname(os.path.abspath(__file__))}/generate.so").eval
fast_eval.restype = c_double


def evaluate(expression: str) -> int | float:
    """
    Evaluates a simple maths expression with only +/-/*/'/'/().
    Order of operations followed.
    
    Calls fast corresponding function written in C++
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
    Converts seconds to HH:MM:SS format
    """
    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return "{}:{}:{}".format(
        *(str(t).zfill(2) for t in (hours, minutes, seconds)))


def bool_to_state(expression: bool) -> str:
    """
    Returns 'normal' if expression evaluates to True,
    else 'disabled'.
    """
    return "normal" if expression else "disabled"