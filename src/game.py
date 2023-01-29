"""
Module of the main game itself.
"""
import ctypes
import itertools
import json
import math
import secrets
import time
import tkinter as tk
from timeit import default_timer as timer
from tkinter import messagebox

import end
import menu
from utils.colours import *
from utils.io import check_folder_exists, FOLDER
from utils.utils import (
    draw_circle, evaluate, bool_to_state, get_sfx, get_music, ink_free,
    seconds_to_hhmmss, load_cpp_library, machine_expression)
from mechanics.achievements import (
    format_special_achievement, get_achievement_count,
    complete_special_achievement)
from mechanics.options import get_option, get_options


NUMBER_COUNT = 7
MAX_SMALL_COUNT = 5
MAX_BIG_COUNT = 5

POSSIBLE_SMALL_NUMBERS = list(range(2, 10))
POSSIBLE_BIG_NUMBERS = [25, 50, 75, 100] * 2

SELECT_SFX = get_sfx("select.wav")
COUNT_SFX = get_sfx("count.wav")
GO_SFX = get_sfx("go.wav")
INCORRECT_SOLUTION_SFX = get_sfx("incorrect.mp3")
CORRECT_SOLUTION_SFX = get_sfx("correct.mp3")

AUTO_SELECT_DELAY_MS = 500

SHUFFLES_BEFORE_REAL_NUMBER = 25
SHUFFLE_DELAY_MS = 50

COUNTDOWN_REFRESH_RATE_MS = 25

DURATION_S = 30

MAX_SOLUTION_LENGTH = 64

# For keybinds whilst entering the solution.
KEY_TO_ACTUAL = {
    "plus": "+",
    "minus": "-",
    "asterisk": "x",
    "slash": "÷",
    "parenleft": "(",
    "parenright": ")"
}

RECENT_NUMBERS_FILE = f"{FOLDER}/recent_numbers.json"
MAX_RECENT_NUMBERS_COUNT = 25


_generate_number = load_cpp_library("generate.so").generate_number
_generate_number.restype = ctypes.c_int


def generate_number(numbers: list[int]) -> int:
    """
    Gets a random target number from 201 to 999.
    """
    recent = get_recent_numbers()
    result = _generate_number(
        (ctypes.c_int * NUMBER_COUNT)(*numbers),
        (ctypes.c_int * len(recent))(*recent), len(recent))
    add_recent_number(result)
    return result


@check_folder_exists()
def get_recent_numbers() -> list[int]:
    """
    Gets the most recently randomly generated target numbers.
    """
    try:
        with open(RECENT_NUMBERS_FILE, "r", encoding="utf8") as f:
            recent = json.load(f)
        if (
            not isinstance(recent, list)
            or len(recent) > MAX_RECENT_NUMBERS_COUNT
            or not all(
                isinstance(number, int) and 201 <= number <= 999
                for number in recent)
        ):
            raise ValueError
        return recent
    except (FileNotFoundError, ValueError):
        with open(RECENT_NUMBERS_FILE, "w", encoding="utf8") as f:
            json.dump([], f)
        return []


@check_folder_exists()
def add_recent_number(number: int) -> None:
    """
    Adds a randomly generated target number to the recent numbers.
    """
    recent = [number] + get_recent_numbers()
    if len(recent) > MAX_RECENT_NUMBERS_COUNT:
        recent.pop()
    with open(RECENT_NUMBERS_FILE, "w", encoding="utf8") as f:
        json.dump(recent, f)


class Game(tk.Frame):
    """
    Holds the actual countdown game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Game")
        self.starting_achievement_count = get_achievement_count()

        options = get_options()
        for sfx in (
            SELECT_SFX, COUNT_SFX, GO_SFX, INCORRECT_SOLUTION_SFX,
            CORRECT_SOLUTION_SFX
        ):
            sfx.set_volume(options["sfx"])
        self.music = get_music(options["music"]["countdown"])
        self.music.set_volume(options["music"]["on"])

        self.frame = SelectNumbersFrame(self)
        self.frame.pack()

    def home(self) -> None:
        """
        Return back to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()

    def start(self) -> None:
        """
        Starts the game.
        """
        SELECT_SFX.stop()
        numbers = [
            int(label.cget("text"))
            for label in self.frame.selected_numbers_frame.number_labels]
        self.start_time = time.time()
        self.frame.destroy()
        self.frame = CountdownFrame(self, numbers)
        self.frame.pack()

    def end(self) -> None:
        """
        Ends the round, leading the player to enter a solution.
        """
        self.music.stop()
        numbers = self.frame.numbers
        target = self.frame.target
        self.frame.destroy()
        self.frame = EnterSolutionFrame(self, numbers, target)
        self.frame.pack()

    def proceed_to_finish(
        self, solution: str | None, numbers: list[int], target: int) -> None:
        """
        After solution entry (if any), proceed to finish.
        """
        self.destroy()
        self.root.unbind("<Key>")
        stop_time = time.time()
        end.GameEnd(
            self.root, solution, numbers, target, self.start_time, stop_time,
            self.starting_achievement_count).pack()


class SelectNumbersFrame(tk.Frame):
    """
    Allows the play to select numbers to be used, either:
    - Big (25, 50, 75, 100)
    - Small (2-9)

    Minimum two of each, total 7.
    """

    def __init__(self, master: Game) -> None:
        super().__init__(master)
        self.master = master
        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Select Numbers")
        self.selected_numbers_frame = SelectedNumbersFrame(self)
        self.small_numbers_frame = SmallNumbersFrame(self)
        self.big_numbers_frame = BigNumbersFrame(self)
        self.navigation_frame = SelectNumbersNavigationFrame(self)

        auto_select = get_option("auto_generate")
        if auto_select["on"]:
            small_count = secrets.choice(range(auto_select["min_small"], 6))
            self.auto_select(small_count, NUMBER_COUNT - small_count)

        self.title_label.pack(padx=10, pady=10)
        self.selected_numbers_frame.pack(padx=10, pady=10)
        self.small_numbers_frame.pack(padx=10, pady=10)
        self.big_numbers_frame.pack(padx=10, pady=10)
        self.navigation_frame.pack(padx=10, pady=(50, 10))

    def add_number(self, number: int) -> None:
        """
        Adds a number to the selection.
        """
        count = self.selected_numbers_frame.count
        self.selected_numbers_frame.number_labels[count].config(text=number)
        self.selected_numbers_frame.count += 1
        SELECT_SFX.play()
        if self.selected_numbers_frame.count == NUMBER_COUNT:
            # Ready to begin - all numbers selected.
            self.small_numbers_frame.destroy()
            self.big_numbers_frame.destroy()
            self.navigation_frame.start_button.config(state="normal")

    def auto_select(self, small_remaining: int, big_remaining: int) -> None:
        """
        Automatically selects numbers (from options).
        """
        if not small_remaining and not big_remaining:
            # No more numbers to select. Exit.
            return
        if not small_remaining:
            # Only big numbers remain.
            self.big_numbers_frame.select()
            big_remaining -= 1
        elif not big_remaining:
            # Only small numbers remain.
            self.small_numbers_frame.select()
            small_remaining -= 1
        else:
            to_select = secrets.choice(("small", "big"))
            if to_select == "small":
                self.small_numbers_frame.select()
                small_remaining -= 1
            else:
                self.big_numbers_frame.select()
                big_remaining -= 1
        self.after(
            AUTO_SELECT_DELAY_MS, lambda: self.auto_select(
                small_remaining, big_remaining))


class SelectedNumbersFrame(tk.Frame):
    """
    Holds the numbers which are selected randomly.
    """

    def __init__(
        self, master: tk.Frame, numbers: list[int] | None = None
    ) -> None:
        super().__init__(master)
        self.number_labels = [
            tk.Label(
                self, font=ink_free(50), width=4, height=1, bg=LIGHT_BLUE,
                highlightbackground=BLACK, highlightthickness=3)
            for _ in range(NUMBER_COUNT)]

        if numbers is not None:
            self.count = NUMBER_COUNT
            for label, number in zip(self.number_labels, numbers):
                label.config(text=number)
                label.pack(padx=5, side="left")
        else:
            self.count = 0
            for label in self.number_labels:
                label.pack(padx=5, side="left")


class SmallNumbersFrame(tk.Frame):
    """
    Holds the small numbers which can be selected.
    """

    def __init__(self, master: SelectNumbersFrame) -> None:
        super().__init__(master, width=1000, height=100)
        self.pack_propagate(False)
        self.master = master

        possible = POSSIBLE_SMALL_NUMBERS.copy()
        self.numbers = []

        for _ in range(MAX_SMALL_COUNT):
            selected = secrets.choice(possible)
            self.numbers.append(selected)
            possible.remove(selected)

        self.info_label = tk.Label(
            self, font=ink_free(25, True), text="Small numbers (2-9):",
            width=25, justify="left")

        auto_select = get_option("auto_generate", "on")
        self.buttons = [
            tk.Button(
                self, bg=ORANGE, activebackground=GREEN,
                width=10, height=5, border=5, command=self.select,
                state=bool_to_state(not auto_select))
            for _ in range(MAX_SMALL_COUNT)]

        self.info_label.pack(side="left")
        for button in self.buttons:
            button.pack(padx=10, side="left")

    def select(self) -> None:
        """
        Selects a small number.
        """
        self.master.add_number(self.numbers.pop())
        self.buttons.pop().destroy()


class BigNumbersFrame(tk.Frame):
    """
    Holds the big numbers which can be selected.
    """

    def __init__(self, master: SelectNumbersFrame) -> None:
        super().__init__(master, width=1000, height=100)
        self.pack_propagate(False)
        self.master = master

        possible = POSSIBLE_BIG_NUMBERS.copy()
        self.numbers = []
        for _ in range(MAX_BIG_COUNT):
            selected = secrets.choice(possible)
            self.numbers.append(selected)
            possible.remove(selected)

        self.info_label = tk.Label(
            self, font=ink_free(25, True), width=25,
            text="Big numbers (25, 50, 75, 100):", justify="left")

        auto_select = get_option("auto_generate", "on")
        self.buttons = [
            tk.Button(
                self, bg=ORANGE, activebackground=GREEN,
                width=10, height=5, border=5, command=self.select,
                state=bool_to_state(not auto_select))
            for _ in range(MAX_BIG_COUNT)]

        self.info_label.pack(side="left")
        for button in self.buttons:
            button.pack(padx=10, side="left")

    def select(self) -> None:
        """
        Selects a big number.
        """
        self.master.add_number(self.numbers.pop())
        self.buttons.pop().destroy()


class SelectNumbersNavigationFrame(tk.Frame):
    """
    Navigation of the select numbers frame.
    """

    def __init__(self, master: SelectNumbersFrame) -> None:
        super().__init__(master)
        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back",
            bg=ORANGE, activebackground=RED, width=10, border=5,
            command=master.master.home)
        self.start_button = tk.Button(
            self, font=ink_free(25), text="Start!",
            bg=ORANGE, activebackground=GREEN, width=10, border=5,
            command=master.master.start, state="disabled")

        self.back_button.pack(padx=10, side="left")
        self.start_button.pack(padx=10, side="right")


class CountdownFrame(tk.Frame):
    """
    Once the player starts, this frame is used to display
    the target number, and once time is up,
    the player is automatically redirected to enter their solution.
    """

    def __init__(self, master: Game, numbers: list[int]) -> None:
        super().__init__(master)
        self.master = master
        self.numbers = numbers
        # Start with the countdown.
        # See self.start for the widgets of the actual round in action.
        self.pre_countdown(3, True)

    def pre_countdown(self, seconds: int, first: bool = False) -> None:
        """
        Count down and then display GO and start.
        """
        if first:
            self.pre_countdown_label = tk.Label(
                self, font=ink_free(200), width=3)
            self.pre_countdown_label.pack(padx=100, pady=100)
        elif seconds == 0:
            COUNT_SFX.stop()
            GO_SFX.play()
            self.pre_countdown_label.config(text="GO!")
            # Starts from here.
            self.after(1000, self.start)
            return

        COUNT_SFX.stop()
        COUNT_SFX.play()

        self.pre_countdown_label.config(text=seconds)
        self.after(1000, lambda: self.pre_countdown(seconds - 1))

    def start(self) -> None:
        """
        Begins the countdown round.
        """
        self.pre_countdown_label.destroy()
        GO_SFX.stop()
        self.target = generate_number(self.numbers)

        self.target_number_label = TargetNumberLabel(self, self.target, True)
        self.selected_numbers_frame = SelectedNumbersFrame(self, self.numbers)
        self.countdown_clock = CountdownClock(self)

        self.target_number_label.pack(padx=25, pady=15)
        self.selected_numbers_frame.pack(padx=10, pady=15)
        self.countdown_clock.pack(padx=10, pady=15)

    def count_down(self, first: bool = False) -> None:
        """
        Starts the 30 second timer and continues to pass the time.
        Once time is up, the player is directed to enter a solution.
        """
        if first:
            self.start_time = timer()
            self.master.music.play()
        else:
            time_passed = timer() - self.start_time
            if time_passed >= DURATION_S:
                return self.master.end()
            self.countdown_clock.destroy()
            # Refresh the clock.
            self.countdown_clock = CountdownClock(self, time_passed)
            self.countdown_clock.pack(padx=10, pady=15)
        self.after(COUNTDOWN_REFRESH_RATE_MS, self.count_down)


class TargetNumberLabel(tk.Label):
    """
    Holds the number the player must try and get.
    """

    def __init__(
        self, master: tk.Frame, number: int, shuffle: bool = False
    ) -> None:
        super().__init__(
            master, font=ink_free(100, True), width=4, bg=GREEN,
            highlightbackground=BLACK, highlightthickness=5)
        self.master = master
        self.number = number
        if shuffle:
            self.shuffle_number_display(SHUFFLES_BEFORE_REAL_NUMBER)
        else:
            self.config(text=number)

    def shuffle_number_display(self, count: int) -> None:
        """
        Displays random numbers which change rapidly.
        Then, the 30 second countdown begins.
        """
        if count:
            self.config(text=secrets.choice(range(201, 1000)))
            self.after(
                SHUFFLE_DELAY_MS,
                lambda: self.shuffle_number_display(count - 1))
        else:
            # Shuffle complete, begin countdown here.
            self.config(text=self.number)
            self.master.count_down(True)


class CountdownClock(tk.Canvas):
    """
    Displays the time remaining for the player to form a solution
    before automatically being directed to enter a solution.
    """

    def __init__(
        self, master: CountdownFrame, seconds_passed: float = 0
    ) -> None:
        super().__init__(master, width=250, height=250)
        self.radius = 123
        self.centx = 125
        self.centy = 125
        # 1 degree = 1/6 of a second (30 seconds total, 180 degrees).
        self.angle = int(seconds_passed * 6)

        draw_circle(self, self.centx, self.centy, self.radius, SILVER)
        self.create_progress_arc()
        self.create_clock_parts()
        self.create_indicators()
        self.create_countdown_pointer()
    
    def create_progress_arc(self) -> None:
        """
        Creates an arc displaying the time passed with an
        appropriate colour selected.
        """
        start = (
            90 - self.angle if self.angle <= 90 else 360 - (self.angle - 90))
        # Green means plenty of time left,  red means time's nearly up!
        arc_fill = CLOCK_COLOURS[
            max(0, int(self.angle / 180 * len(CLOCK_COLOURS)) - 1)]
        self.create_arc(
            3, 3, 247, 247, start=start, extent=self.angle,
            fill=arc_fill, outline="")
    
    def create_clock_parts(self) -> None:
        """
        Create the main parts of the clock which never change in any way.
        """
        draw_circle(self, self.centx, self.centy, 60, SILVER, "")
        self.create_line(self.centx, 0, self.centx, 250, fill=BLACK, width=2)
        self.create_line(0, self.centy, 250, self.centy, fill=BLACK)
        draw_circle(self, self.centx, self.centy, 15, GREY, "")
    
    def create_indicators(self) -> None:
        """
        Create indicators (5, 10, 20, 25, 35, 40, 50, 55).
        """
        # For 5, 25, 35 and 55.
        steep_gradient_max_x = self.radius * math.cos(math.radians(60))
        steep_gradient_max_y = (
            self.radius ** 2 - steep_gradient_max_x ** 2) ** 0.5

        # For 10, 20, 40, 50
        gentle_gradient_max_x = self.radius * math.cos(math.radians(30))
        gentle_gradient_max_y = (
            self.radius ** 2 - gentle_gradient_max_x ** 2) ** 0.5

        for max_x, max_y in (
            (steep_gradient_max_x, steep_gradient_max_y),
            (gentle_gradient_max_x, gentle_gradient_max_y)
        ):
            for x_op, y_op in itertools.product("+-", repeat=2):
                if x_op == "+":
                    x1 = self.centx + 100/self.radius * max_x
                    x2 = self.centx + 120/self.radius * max_x
                else:
                    x1 = self.centx - 100/self.radius * max_x
                    x2 = self.centx - 120/self.radius * max_x
                if y_op == "+":
                    y1 = self.centy + 100/self.radius * max_y
                    y2 = self.centy + 120/self.radius * max_y
                else:
                    y1 = self.centy - 100/self.radius * max_y
                    y2 = self.centy - 120/self.radius * max_y

                # White if passed.
                if (
                    max_x == steep_gradient_max_x and x_op == "+" and
                    (
                        (y_op == "-" and self.angle > 30) or
                        (y_op == "+" and self.angle > 150))
                ) or (
                    max_x == gentle_gradient_max_x and x_op == "+" and
                    (
                        (y_op == "-" and self.angle > 60) or
                        (y_op == "+" and self.angle > 120))
                ):
                    self.create_line(x1, y1, x2, y2, fill=WHITE)
                else:
                    self.create_line(x1, y1, x2, y2, fill=BLACK)
    
    def create_countdown_pointer(self) -> None:
        """
        Creates the countdown pointer.
        """
        if self.angle == 0:
            self.create_polygon(
                self.centx - 10, self.centy,
                self.centx + 10, self.centy, self.centx, 0, fill=GREY)
        elif self.angle == 90:
            self.create_polygon(
                self.centx, self.centy - 10, self.centx, self.centy + 10,
                self.centx + self.radius, self.centy, fill=GREY)
        elif self.angle == 180:
            self.create_polygon(
                self.centx - 10, self.centy, self.centx + 10, self.centy,
                self.centx, self.centy + self.radius, fill=GREY)
        else:
            if self.angle < 90:
                x_shift = 10 * math.cos(math.radians(self.angle))
                y_shift = (10 ** 2 - x_shift ** 2) ** 0.5

                x_right = self.radius * math.cos(
                    math.radians(90 - self.angle))
                y_up = (self.radius ** 2 - x_right ** 2) ** 0.5

                self.create_polygon(
                    self.centx - x_shift, self.centy - y_shift,
                    self.centx + x_shift, self.centy + y_shift,
                    self.centx + x_right, self.centy - y_up, fill=GREY)
            else:
                x_shift = 10 * math.sin(math.radians(self.angle - 90))
                y_shift = (100 - x_shift ** 2) ** 0.5

                x_right = self.radius * math.cos(
                    math.radians(self.angle - 90))
                y_down = (self.radius ** 2 - x_right ** 2) ** 0.5

                self.create_polygon(
                    self.centx + x_shift, self.centy - y_shift,
                    self.centx - x_shift, self.centy + y_shift,
                    self.centx + x_right, self.centy + y_down, fill=GREY)


class EnterSolutionFrame(tk.Frame):
    """
    Where the player enters a solution with their selected numbers
    for the target.
    """

    def __init__(self, master: Game, numbers: list[int], target: int) -> None:
        super().__init__(master)
        self.master = master
        self.numbers = numbers
        self.target = target
        option = get_option("solution_time_limit")
        self.start = timer()
        self.max_seconds = (
            option["minutes"] * 60 if option["on"] else float("inf"))

        self.title_label = tk.Label(
            self, font=ink_free(50, True), text="Enter your best solution!")
        if option["on"]:
            self.time_left_label = tk.Label(
                self, font=ink_free(25), width=25,
                text=f"Time left: {seconds_to_hhmmss(self.max_seconds)}")
        self.solution_label = SolutionLabel(self)
        self.solution_buttons = SolutionButtonsFrame(self)
        self.option_buttons = EnterSolutionOptionsFrame(self)

        self.used_numbers = []
        self.opening_parentheses = 0
        self.closing_parentheses = 0

        self.title_label.pack(padx=25, pady=15)
        if option["on"]:
            self.time_left_label.pack(padx=10, pady=10)
            self.update_time_remaining()
        self.solution_label.pack(padx=10, pady=10)
        self.solution_buttons.pack(padx=10, pady=10)
        self.option_buttons.pack(padx=10, pady=(50, 10))

        self.master.root.bind("<Key>", self.enter_key)

    def add(self, to_add: str, from_pop: bool = False) -> None:
        """
        Adds a number, operator or parenthesis to the solution.
        """
        current_solution = self.solution_label.get()
        # Automatically add 'x' sign to indicate multiplication
        # if a number or ) is followed by (
        if (
            current_solution and to_add == "("
            and (
                current_solution[-1].isdigit()
                or current_solution[-1] == ")")
        ):
            if len(current_solution) >= MAX_SOLUTION_LENGTH - 1:
                # Cannot insert two more characters 'x('
                return
            new_solution = f"{current_solution}x{to_add}"
        else:
            if len(current_solution) > MAX_SOLUTION_LENGTH - len(to_add):
                # Cannot insert n more characters.
                return
            new_solution = current_solution + to_add

        self.solution_label.config(text=new_solution)

        if to_add.isdigit() or to_add == ")":
            # Next, an operator or closing parenthesis is expected.
            for button in self.solution_buttons:
                button.config(
                    state=bool_to_state(not button.cget("text").isdigit()))
        else:
            # Next, a number or opening parenthesis is expected.
            for button in self.solution_buttons:
                button.config(
                    state=bool_to_state(
                        button.cget("text").isdigit()
                        or button.cget("text") == "("))

        if to_add.isdigit() and not from_pop:
            self.used_numbers.append(to_add)

        affected_buttons = []
        for number in self.used_numbers:
            for button in self.solution_buttons:
                # Disables used numbers in grey instead of red.
                if (
                    button.cget("text") == number
                    and button not in affected_buttons
                ):
                    affected_buttons.append(button)
                    if (
                        button.cget("disabledforeground") != GREY
                        or button.cget("state") == "normal"
                    ):
                        button.config(
                            state="disabled", disabledforeground=GREY)
                    break

        # Disable all except closing parenthesis or remove last input.
        if len(self.used_numbers) == NUMBER_COUNT:
            for button in self.solution_buttons:
                button.config(
                    state=bool_to_state(button.cget("text") in ")←"))

        if to_add == "(" and not from_pop:
            self.opening_parentheses += 1
        elif to_add == ")" and not from_pop:
            self.closing_parentheses += 1

        if self.closing_parentheses >= self.opening_parentheses:
            # Cannot add closing parentheses with no corresponding
            # opening parentheses.
            closing_parentheses_button = self.solution_buttons.buttons[1][-2]
            closing_parentheses_button.config(state="disabled")

        back_button = self.solution_buttons.buttons[1][-1]
        back_button.config(state="normal")

        self.option_buttons.reset_button.config(state="normal")
        self.option_buttons.submit_button.config(
            state=bool_to_state(
                self.opening_parentheses == self.closing_parentheses
                and (to_add.isdigit() or to_add == ")")))

    def pop(self) -> None:
        """
        Removes the previous input from the solution.
        """
        # Gets last input: either a number, operator or parenthesis.
        current_solution = self.solution_label.get()
        if not current_solution:
            return

        index = -1
        while current_solution[index].isdigit():
            if abs(index) >= len(current_solution):
                break
            index -= 1
        else:
            index = min(index + 1, -1)

        to_remove = current_solution[index:]
        if to_remove.isdigit():
            # Removes number from used numbers as needed.
            self.used_numbers.remove(to_remove)
            for button in self.solution_buttons:
                if (
                    button.cget("state") == "disabled"
                    and button.cget("text") == to_remove
                ):
                    button.config(disabledforeground=RED)
        elif to_remove == "(":
            self.opening_parentheses -= 1
        elif to_remove == ")":
            self.closing_parentheses -= 1

        new_solution = current_solution[:index]
        if not new_solution:
            self.reset()
            return

        # Re-adds input before the removed input. Not much new code needed.
        index = -1
        while new_solution[index].isdigit():
            if abs(index) >= len(new_solution):
                break
            index -= 1
        else:
            index = min(index + 1, -1)

        self.solution_label.config(text=new_solution[:index])
        self.add(new_solution[index:], True)

    def reset(self) -> None:
        """
        Resets solution input.
        """
        self.used_numbers = []
        self.opening_parentheses = 0
        self.closing_parentheses = 0

        self.solution_label.config(text="")
        for button in self.solution_buttons:
            button.config(
                state=bool_to_state(
                    button.cget("text").isdigit()
                    or button.cget("text") == "("), disabledforeground=RED)

        self.option_buttons.reset_button.config(state="disabled")
        self.option_buttons.submit_button.config(state="disabled")

    def enter_key(self, event: tk.Event) -> None:
        """
        Takes a key which represents an operator, single-digit number
        or parenthesis, and if the corresponding button is enabled,
        the key is added.
        """
        key = event.keysym.lower()
        if key in ("backspace", "left"):
            self.pop()
            return

        # If key is not already the actual key, convert to it.
        key = KEY_TO_ACTUAL.get(key, key)

        for button in self.solution_buttons:
            if button.cget("text") == key:
                if button.cget("state") == "normal":
                    self.add(key)
                return

    def submit(self) -> None:
        """
        Gets a solution from the player and validates it.
        If correct, the player wins, or else they will be told
        the solution is incorrect/invalid.
        """
        solution = self.solution_label.get()
        to_evaluate = machine_expression(solution)
        INCORRECT_SOLUTION_SFX.stop()

        if evaluate(to_evaluate) == self.target:
            CORRECT_SOLUTION_SFX.play()
            self.master.proceed_to_finish(solution, self.numbers, self.target)
        else:
            if (
                get_option("stats") and
                complete_special_achievement("incorrect_solution")
            ):
                messagebox.showinfo(
                    "Achievement!",
                    format_special_achievement("incorrect_solution"))
            INCORRECT_SOLUTION_SFX.play()

    def skip(self) -> None:
        """
        If the player has no solution, they can skip solution entry.
        This will be counted as a loss.
        """
        self.master.proceed_to_finish(None, self.numbers, self.target)

    def update_time_remaining(self) -> None:
        """
        Updates the time remaining. If time is up, the solution
        will be skipped and the round will count as a loss.
        """
        seconds_remaining = self.max_seconds - (timer() - self.start)
        if seconds_remaining <= 0:
            self.skip()
            return
        self.time_left_label.config(
            text=f"Time left: {seconds_to_hhmmss(seconds_remaining)}")
        self.after(10, self.update_time_remaining)


class SolutionLabel(tk.Label):
    """
    Where the player sees the solution they input.
    """

    def __init__(self, master: EnterSolutionFrame) -> None:
        super().__init__(
            master, font=ink_free(20),
            width=MAX_SOLUTION_LENGTH + 1, height=2, bg=GREEN,
            highlightbackground=BLACK, highlightthickness=5)

    def get(self) -> str:
        """
        Returns current solution entry.
        """
        return self.cget("text")


class SolutionButtonsFrame(tk.Frame):
    """
    Add or remove numbers, operators and parentheses to the solution.
    """

    def __init__(self, master: EnterSolutionFrame) -> None:
        super().__init__(master)
        self.master = master
        self.buttons = [] # In rows.

        self.buttons.append([
            SolutionInputButton(self, str(number))
            for number in master.numbers])

        row_2 = [SolutionInputButton(self, char) for char in "+-x÷()"]
        back_button = tk.Button(
            self, font=ink_free(25), text="←", width=4, border=3, bg=GREY,
            activebackground=RED, disabledforeground=RED, command=master.pop)
        row_2.append(back_button)

        for button in row_2:
            if button.cget("text") != "(":
                button.config(state="disabled")

        self.buttons.append(row_2)

        for i, row in enumerate(self.buttons):
            for j, button in enumerate(row):
                button.grid(row=i, column=j, padx=5, pady=5)

    def __iter__(self) -> None:
        """
        Allows iteration over all buttons in all rows.
        """
        for row in self.buttons:
            for button in row:
                yield button


class SolutionInputButton(tk.Button):
    """
    Adds a number, operator or parenthesis to the solution.
    Obviously, each number can only be used once.
    """

    def __init__(self, master: SolutionButtonsFrame, to_add: str) -> None:
        super().__init__(
            master, font=ink_free(25), text=to_add, width=4, border=3,
            bg=ORANGE, activebackground=GREEN, disabledforeground=RED,
            command=lambda: master.master.add(to_add))


class EnterSolutionOptionsFrame(tk.Frame):
    """
    Holds buttons which include:
    - Allowing the player to reset the solution input
    - Submitting a solution
    - Proceed without a solution (no solution found)
    """

    def __init__(self, master: EnterSolutionFrame) -> None:
        super().__init__(master)
        self.reset_button = tk.Button(
            self, font=ink_free(25), text="Reset", width=10, border=5,
            bg=ORANGE, activebackground=RED, state="disabled",
            command=master.reset)
        self.submit_button = tk.Button(
            self, font=ink_free(25), text="Submit", width=10, border=10,
            bg=ORANGE, activebackground=GREEN, state="disabled",
            command=master.submit)
        self.skip_button = tk.Button(
            self, font=ink_free(25), text="No solution", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=master.skip)

        self.reset_button.pack(padx=10, side="left")
        self.submit_button.pack(padx=10, side="left")
        self.skip_button.pack(padx=10)
