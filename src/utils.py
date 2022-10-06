import tkinter as tk
import os
from ctypes import cdll, c_double


evallib = cdll.LoadLibrary(
    f"{os.path.dirname(os.path.abspath(__file__))}/eval.so")
evallib.eval.restype = c_double


def evaluate(expression: str) -> int | float:
    """
    Evaluates a simple maths expression with only +/-/*/'/'/().
    Order of operations followed.
    
    Calls fast corresponding function written in C++
    """
    result = evallib.eval(expression.encode(), 0, -1)
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