"""
Handles generation of solutions with the usable numbers
along with a target number, with certain settings allowed.
"""
import ctypes
import itertools
import os
import secrets
import string
import threading
import tkinter as tk
from contextlib import suppress
from timeit import default_timer as timer
from typing import Literal

import game
from utils.colours import *
from utils.io import TEMPORARY_FOLDER, create_temp_folder
from utils.utils import (
    get_sfx, ink_free, load_cpp_library, human_expression, machine_expression)
from .options import get_option


OPERATORS = "+-x÷"

MIN_SOLUTION_NUMBER_COUNT = 4
MAX_SOLUTION_NUMBER_COUNT = 7

MIN_SOLUTION_COUNT = 1
MAX_SOLUTION_COUNT = 100
DEFAULT_SOLUTION_COUNT = 10

SOLUTION_PARENTHESES_OPTIONS = ("Allow nested", "Disallow nested", "OFF")
DEFAULT_SOLUTION_PARENTHESES_OPTION = 0 # Disallow nested.

MIN_SOLUTIONS_SECONDS = 1
MAX_SOLUTIONS_SECONDS = 60
DEFAULT_SOLUTIONS_SECONDS = 10

SOLUTION_FOUND_SFX = get_sfx("solutionfound.wav")
NO_SOLUTION_FOUND_SFX = get_sfx("nosolutionfound.wav")

POSSIBLE_SOLUTION_FILENAME_CHARACTERS = string.digits + string.ascii_lowercase
SOLUTION_FILENAME_LENGTH = 12


get_solution = load_cpp_library("generate.so").get_solution
get_solution.restype = ctypes.c_double


class SolutionGenerationSettings:
    """
    Holds the settings of what types of solutions are generated
    and the time limit for generation.
    """

    def __init__(
        self, min_number_count: int, max_number_count: int,
        max_solution_count: int, nested_parentheses: bool | None,
        operators: str, seconds_limit: int
    ) -> None:
        self.min_number_count = min_number_count
        self.max_number_count = max_number_count
        self.max_solution_count = max_solution_count
        self.parentheses_option = (
            nested_parentheses if nested_parentheses is not None else -1)
        self.operators = operators
        self.seconds_limit = seconds_limit
        # In case generation is aborted.
        self.cancel = False


def generate_solutions(
    numbers: list[int], target: int,
    settings: SolutionGenerationSettings) -> list[str]:
    """
    Gets solutions for a given target number with particular smaller
    numbers based on certain settings.
    """
    if not settings.operators:
        return []
    start = timer()
    solutions = []
    # Uniform probability for n numbers to be tried.
    perms = [
        list(itertools.permutations(numbers, count))
        for count in range(
            settings.min_number_count, settings.max_number_count + 1)]
    operators = ctypes.c_char_p(settings.operators.encode())

    while (
        timer() - start < settings.seconds_limit
        and perms and len(solutions) < settings.max_solution_count
    ):
        count_choice = secrets.choice(perms)
        choice = secrets.choice(count_choice)
        perms[perms.index(count_choice)].remove(choice)
        filename = "".join(
            secrets.choice(POSSIBLE_SOLUTION_FILENAME_CHARACTERS)
            for _ in range(SOLUTION_FILENAME_LENGTH))
        file_path = f"{TEMPORARY_FOLDER}/{filename}"

        if [] in perms:
            perms.remove([])

        create_temp_folder()
        get_solution(
            (ctypes.c_int * len(choice))(*choice), len(choice), target,
            operators, settings.parentheses_option, file_path.encode())

        with suppress(FileNotFoundError):
            with open(file_path, "r", encoding="utf8") as f:
                solution = f.read()
            solutions.append(human_expression(solution))
            os.remove(file_path)
        if settings.cancel:
            return []

    return solutions if not settings.cancel else []


class SolutionsFrame(tk.Frame):
    """
    Holds the GUI which allows the player to get solutions
    for a particular target number using smaller numbers,
    with certain criteria which can be set.
    Serves as an extension to another part of the GUI.
    """

    def __init__(
        self, root: tk.Tk, corresponding_frame: tk.Frame,
        numbers: list[int], target: int
    ) -> None:
        super().__init__(root)
        self.root = root
        self.frame = corresponding_frame
        self.numbers = numbers
        self.target = target
        self.settings = None

        for sfx in (SOLUTION_FOUND_SFX, NO_SOLUTION_FOUND_SFX):
            sfx.set_volume(get_option("sfx"))

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Solutions")
        self.selected_numbers_frame = game.SelectedNumbersFrame(
            self, self.numbers)
        self.target_number_label = game.TargetNumberLabel(self, self.target)
        self.solutions_options_frame = SolutionsOptionsFrame(self)
        self.solutions_listbox = tk.Listbox(
            self, font=ink_free(15), width=25, height=10, bg=GREEN, border=5)
        self.navigation_frame = SolutionsNavigationFrame(self)

        self.title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5)
        self.selected_numbers_frame.grid(
            row=1, column=0, columnspan=3, padx=10, pady=5)
        self.target_number_label.grid(
            row=2, column=0, padx=10, pady=10, sticky="w")
        self.solutions_options_frame.grid(
            row=2, column=1, padx=10, pady=5, sticky="w")
        self.solutions_listbox.grid(row=2, column=2, padx=10, pady=5)
        self.navigation_frame.grid(
            row=3, column=0, columnspan=3, padx=10, pady=10)

    def generate(self) -> None:
        """
        Generates solutions and displays them in the listbox.
        """
        options = self.solutions_options_frame
        min_number_count = options.min_number_count_frame.count.get()
        max_number_count = options.max_number_count_frame.count.get()
        max_solution_count = options.max_solution_count_frame.count.get()

        parentheses = options.parentheses_frame.option.get()
        nested_parentheses = parentheses if parentheses != -1 else None

        operators = machine_expression(
            "".join(
            operator for operator, state in (
                options.operators_frame.operators.items()) if state.get()))
        seconds_limit = options.seconds_limit_frame.seconds.get()

        settings = SolutionGenerationSettings(
                min_number_count, max_number_count, max_solution_count,
                nested_parentheses, operators, seconds_limit)
        self.settings = settings

        SOLUTION_FOUND_SFX.stop()
        NO_SOLUTION_FOUND_SFX.stop()
        self.solutions_listbox.delete(0, "end")
        self.navigation_frame.cancel_generate_button()

        solutions = generate_solutions(self.numbers, self.target, settings)
        if self.settings is None:
            return
        self.navigation_frame.reset_generate_button()
        if solutions:
            self.solutions_listbox.insert(0, *solutions)
            SOLUTION_FOUND_SFX.play()
        else:
            NO_SOLUTION_FOUND_SFX.play()

    def cancel(self) -> None:
        """
        Cancels generation.
        """
        if self.settings is None:
            # Something weird has happened due to threading. Ignore.
            return
        # Settings cancelled so thread does not return any solutions.
        self.settings.cancel = True
        # Does not affect actual settings object.
        self.settings = None
        self.navigation_frame.reset_generate_button()


class SolutionsOptionsFrame(tk.Frame):
    """
    Allows the player to filter for particular types of solutions:
    - Minimum and maximum number count
    - Maximum solution count
    - Whether to allow nested parentheses or not, if any parentheses at all.
    - Allowed operators (add/subtract/multiply/divide)

    Also ensures the player to set a time limit for how long to search
    for solutions (execution is rather slow with maximum settings...)
    """

    def __init__(self, master: SolutionsFrame) -> None:
        super().__init__(master)
        self.master = master

        self.min_number_count_frame = SolutionNumberCountFrame(self, "min")
        self.max_number_count_frame = SolutionNumberCountFrame(self, "max")
        self.max_solution_count_frame = MaxSolutionsFrame(self)
        self.parentheses_frame = SolutionParenthesesFrame(self)
        self.operators_frame = SolutionOperatorsFrame(self)
        self.seconds_limit_frame = SolutionsSecondsLimitFrame(self)

        self.min_number_count_frame.pack(padx=10)
        self.max_number_count_frame.pack(padx=10)
        self.max_solution_count_frame.pack(padx=10)
        self.parentheses_frame.pack(padx=10)
        self.operators_frame.pack(padx=10)
        self.seconds_limit_frame.pack(padx=10)

    def check_number_counts(self, change: Literal["min", "max"]) -> None:
        """
        Ensures the maximum number count is increased to at least the
        minimum number count if currently lower and that
        the minimum number count is decreased to at least the
        maximum number count if currently higher.
        """
        if change == "min":
            max_count = self.max_number_count_frame.count.get()
            if self.min_number_count_frame.count.get() > max_count:
                self.min_number_count_frame.count.set(max_count)
        else:
            min_count = self.min_number_count_frame.count.get()
            if self.max_number_count_frame.count.get() < min_count:
                self.max_number_count_frame.count.set(min_count)


class SolutionNumberCountFrame(tk.Frame):
    """
    Holds a number count setting (min/max).
    """

    def __init__(
        self, master: SolutionsOptionsFrame, bound: Literal["min", "max"]
    ) -> None:
        super().__init__(master)
        self.bound = bound
        self.label = tk.Label(
            self, font=ink_free(15, True),
            text="{} number count:".format(
                "Minimum" if self.bound == "min" else "Maximum"))
        self.count = tk.IntVar(
            value=MIN_SOLUTION_NUMBER_COUNT if self.bound == "min"
                else MAX_SOLUTION_NUMBER_COUNT)

        self.count_scale = tk.Scale(
            self, font=ink_free(15), length=200,
            from_=MIN_SOLUTION_NUMBER_COUNT, to=MAX_SOLUTION_NUMBER_COUNT,
            orient="horizontal", variable=self.count, sliderlength=50,
            command=lambda _: self.master.check_number_counts(self.bound))

        self.label.pack(side="left", padx=10)
        self.count_scale.pack(padx=10)


class MaxSolutionsFrame(tk.Frame):
    """
    Holds the maximum number of solutions to generate setting.
    """

    def __init__(self, master: SolutionsOptionsFrame) -> None:
        super().__init__(master)
        self.count = tk.IntVar(value=DEFAULT_SOLUTION_COUNT)
        self.label = tk.Label(
            self, font=ink_free(15, True), text="Maximum solution count:")
        self.count_scale = tk.Scale(
            self, font=ink_free(15), length=200, orient="horizontal",
            from_=MIN_SOLUTION_COUNT, to=MAX_SOLUTION_COUNT,
            variable=self.count)

        self.label.pack(side="left", padx=10)
        self.count_scale.pack(padx=10)


class SolutionParenthesesFrame(tk.Frame):
    """
    Holds parentheses settings for solution, either:
    - Nested parentheses allowed
    - Nestead parentheses disallowed
    - No parentheses allowed at all
    """

    def __init__(self, master: SolutionsOptionsFrame) -> None:
        super().__init__(master)
        self.label = tk.Label(
            self, font=ink_free(15, True), text="Parentheses:")
        self.label.pack(side="left", padx=10)
        # 1 - Nested, 0 - No nested, -1 - No parentheses
        self.option = tk.IntVar(value=DEFAULT_SOLUTION_PARENTHESES_OPTION)

        for option, value in zip(
            SOLUTION_PARENTHESES_OPTIONS, range(1, -2, -1)
        ):
            radiobutton = tk.Radiobutton(
                self, font=ink_free(15), text=option,
                variable=self.option, value=value, selectcolor=ORANGE)
            radiobutton.pack(side="left")


class SolutionOperatorsFrame(tk.Frame):
    """
    Holds the setting for which operators a solution can have
    i.e add/subtract/multiply/divide
    """

    def __init__(self, master: SolutionsOptionsFrame) -> None:
        super().__init__(master)
        self.label = tk.Label(
            self, font=ink_free(15, True), text="Operators:")
        self.label.pack(side="left", padx=10)

        self.operators = {
            operator: tk.BooleanVar(value=True) for operator in OPERATORS
        }
        for operator in OPERATORS:
            checkbutton = tk.Checkbutton(
                self, font=ink_free(15), text=operator,
                variable=self.operators[operator], selectcolor=ORANGE)
            checkbutton.pack(side="left", padx=5)


class SolutionsSecondsLimitFrame(tk.Frame):
    """
    Holds the maximum number of seconds to generate solutions for.
    """

    def __init__(self, master: SolutionsOptionsFrame) -> None:
        super().__init__(master)
        self.label = tk.Label(
            self, font=ink_free(15, True),
            text="Maximum seconds to generate for:")
        self.seconds = tk.IntVar(value=DEFAULT_SOLUTIONS_SECONDS)
        self.seconds_scale = tk.Scale(
            self, font=ink_free(15), length=200, orient="horizontal",
            from_=MIN_SOLUTIONS_SECONDS, to=MAX_SOLUTIONS_SECONDS,
            variable=self.seconds)

        self.label.pack(side="left", padx=10)
        self.seconds_scale.pack(padx=10)


class SolutionsNavigationFrame(tk.Frame):
    """
    Holds buttons which allow the player to navigate through the solutions UI.
    """

    def __init__(self, master: SolutionsFrame) -> None:
        super().__init__(master)
        self.master = master
        self.generate_button = tk.Button(
            self, font=ink_free(25), text="Generate", width=15, border=3,
            bg=ORANGE, activebackground=GREEN,
            command=lambda: threading.Thread(
                target=self.master.generate, daemon=True).start())

        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back", width=15, border=3,
            bg=ORANGE, activebackground=GREEN,
            command=master.frame.exit_solutions)

        self.generate_button.pack(side="left", padx=10)
        self.back_button.pack(padx=10)

    def reset_generate_button(self) -> None:
        """
        Resets the generate button to its normal state.
        """
        self.generate_button.config(
            text="Generate", bg=ORANGE, activebackground=GREEN,
            command=lambda: threading.Thread(
                target=self.master.generate, daemon=True).start())

    def cancel_generate_button(self) -> None:
        """
        Temporarily turns the generate button to a cancel button.
        """
        self.generate_button.config(
            text="Cancel", bg=RED, activebackground=RED,
            command=self.master.cancel)
