import tkinter as tk
from tkinter import messagebox
import secrets
import math
import itertools
from timeit import default_timer as timer

import menu
import end
import generate
import audio
from colours import *
from font import ink_free

TITLE = "Countdown - Game"

NUMBER_COUNT = 7
MAX_SMALL_COUNT = MAX_BIG_COUNT = 5

COUNT_SFX = audio.get_sfx("count.wav")
GO_SFX = audio.get_sfx("go.wav")
INCORRECT_SOLUTION_SFX = audio.get_sfx("incorrect.mp3")
CORRECT_SOLUTION_SFX = audio.get_sfx("correct.mp3")
COUNTDOWN_MUSIC = audio.get_music("countdown.wav")

SHUFFLES_BEFORE_REAL_NUMBER = 25
SHUFFLE_DELAY_MS = 50

DURATION_S = 30

MAX_SOLUTION_LENGTH = 64

KEY_TO_ACTUAL = {
    "plus": "+",
    "minus": "-",
    "asterisk": "x",
    "slash": "÷",
    "parenleft": "(",
    "parenright": ")"
}


def draw_circle(
    canvas: tk.Canvas, x: int, y: int, radius: int,
    fill: str | None = None, outline: str = "black") -> None:
    """
    Draws a circle with a given centre and radius onto the canvas.
    """
    canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius,
        fill=fill, outline=outline)


class Game(tk.Frame):
    """
    Holds the actual countdown game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title(TITLE)

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
        numbers = [
            int(label.cget("text"))
            for label in self.frame.selected_numbers_frame.number_labels]
        self.frame.destroy()
        self.frame = CountdownFrame(self, numbers)
        self.frame.pack()

    def end(self) -> None:
        """
        Ends the round, leading the player to enter a solution.
        """
        numbers = self.frame.numbers
        target = self.frame.target
        COUNTDOWN_MUSIC.stop()
        self.frame.destroy()
        self.frame = EnterSolutionFrame(self, numbers, target)
        self.frame.pack()
    
    def proceed_to_finish(self, solution: str | None, target: int) -> None:
        """
        After solution entry (if any), proceed to finish.
        """
        self.destroy()
        self.root.unbind("<Key>")
        end.GameEnd(self.root, solution, target).pack()


class SelectNumbersFrame(tk.Frame):
    """
    Allows the play to select numbers to be used, either:
    - Big (25, 50, 75, 100)
    - Small (1-9)

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
        self.selected_numbers_frame.number_labels[count].config(
            text=number)
        self.selected_numbers_frame.count += 1

        if self.selected_numbers_frame.count == NUMBER_COUNT:
            # Ready to begin - all numbers selected.
            self.small_numbers_frame.destroy()
            self.big_numbers_frame.destroy()
            self.navigation_frame.start_button.config(state="normal")


class SelectedNumbersFrame(tk.Frame):
    """
    Holds the numbers which are selected randomly.
    """

    def __init__(
        self, master: tk.Frame, numbers: list[int] | None = None) -> None:
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
        super().__init__(master)
        self.master = master

        possible = list(range(1, 10))
        self.numbers = []

        for _ in range(MAX_SMALL_COUNT):
            selected = secrets.choice(possible)
            self.numbers.append(selected)
            possible.remove(selected)
        
        self.info_label = tk.Label(
            self, font=ink_free(25, True), text="Small numbers (1-9):",
            justify="left")
        
        self.buttons = [
            tk.Button(
                self, bg=ORANGE, activebackground=GREEN,
                width=10, height=5, border=5, command=self.select)
            for _ in range(MAX_SMALL_COUNT)]
        
        self.info_label.pack(side="left")
        for button in self.buttons:
            button.pack(padx=10, side="right")
    
    def select(self) -> None:
        """
        Selects a small number.
        """
        self.master.add_number(self.numbers.pop())
        self.buttons.pop().destroy()

        if not self.numbers:
            self.destroy()


class BigNumbersFrame(tk.Frame):
    """
    Holds the big numbers which can be selected.
    """

    def __init__(self, master: SelectNumbersFrame) -> None:
        super().__init__(master)
        self.master = master

        possible = [25, 50, 75, 100] * 2
        self.numbers = []
        for _ in range(MAX_BIG_COUNT):
            selected = secrets.choice(possible)
            self.numbers.append(selected)
            possible.remove(selected)

        self.info_label = tk.Label(
            self, font=ink_free(25, True),
            text="Big numbers (25, 50, 75, 100):", justify="left")
        
        self.buttons = [
            tk.Button(
                self, bg=ORANGE, activebackground=GREEN,
                width=10, height=5, border=5, command=self.select)
            for _ in range(MAX_SMALL_COUNT)]
        
        self.info_label.pack(side="left")
        for button in self.buttons:
            button.pack(padx=10, side="right")
    
    def select(self) -> None:
        """
        Selects a big number.
        """
        self.master.add_number(self.numbers.pop())
        self.buttons.pop().destroy()

        if not self.numbers:
            self.destroy()


class SelectNumbersNavigationFrame(tk.Frame):
    """
    Navigation of the select numbers frame.
    """

    def __init__(self, master: SelectNumbersFrame) -> None:
        super().__init__(master)

        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back",
            bg=ORANGE, activebackground=RED, width=10, border=3,
            command=master.master.home)
        self.start_button = tk.Button(
            self, font=ink_free(25), text="Start!",
            bg=ORANGE, activebackground=GREEN, width=10, border=3,
            command=master.master.start, state="disabled")
        
        self.back_button.pack(padx=10, side="left")
        self.start_button.pack(padx=10, side="right")


class CountdownFrame(tk.Frame):
    """
    Once the player starts, this frame is used to display
    the number the player must try and get, and once time is up,
    the player is automatically redirected to enter their solution(s).
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
        self.target = generate.generate_number(self.numbers)

        self.target_number_label = TargetNumberLabel(self, self.target)
        self.selected_numbers_frame = SelectedNumbersFrame(self, self.numbers)
        self.countdown_clock = CountdownClock(self)

        self.target_number_label.pack(padx=25, pady=15)
        self.selected_numbers_frame.pack(padx=10, pady=10)
        self.countdown_clock.pack(padx=10, pady=10)

        self.target_number_label.shuffle_number_display(
            SHUFFLES_BEFORE_REAL_NUMBER)
    
    def count_down(self, first: bool = False) -> None:
        """
        Starts the 30 second timer.
        """
        if first:
            self.start_time = timer()
            COUNTDOWN_MUSIC.play()
        elif timer() - self.start_time >= DURATION_S:
            return self.master.end()
        else:
            self.countdown_clock.destroy()
            time_passed = timer() - self.start_time
            # Refresh the clock.
            self.countdown_clock = CountdownClock(self, time_passed)
            self.countdown_clock.pack(padx=10, pady=10)
        self.after(25, self.count_down)


class TargetNumberLabel(tk.Label):
    """
    Holds the number the player must try and get.
    """

    def __init__(self, master: CountdownFrame, number: int) -> None:
        super().__init__(
            master, font=ink_free(100, True), width=4, bg=GREEN,
            highlightbackground=BLACK, highlightthickness=5)
        self.master = master
        self.number = number
    
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
        self, master: CountdownFrame, seconds_passed: float = 0) -> None:
        super().__init__(master, width=250, height=250)
        radius = 123
        centx = 125
        centy = 125
        draw_circle(self, centx, centy, radius, SILVER)

        # 1 degree = 1/6 of a second.
        angle = int(seconds_passed * 6)

        start = 90 - angle if angle <= 90 else 360 - (angle - 90)
        # Green means plenty of time left,  red means time's nearly up!
        arc_fill = CLOCK_COLOURS[
            max(0, int(angle / 180 * len(CLOCK_COLOURS)) - 1)]
        self.create_arc(
            3, 3, 247, 247, start=start, extent=angle,
            fill=arc_fill, outline="")

        draw_circle(self, centx, centy, 60, SILVER, "")
        self.create_line(centx, 0, centx, 250, fill=BLACK, width=2)
        self.create_line(0, centy, 250, centy, fill=BLACK)
        draw_circle(self, centx, centy, 15, GREY, "")

        # Create indicators (5, 10, 20, 25, 35, 40, 50, 55).

        # For 5, 25, 35 and 55.
        steep_gradient_max_x = radius * math.cos(math.radians(60))
        steep_gradient_max_y = (
            radius ** 2 - steep_gradient_max_x ** 2) ** 0.5

        # For 10, 20, 40, 50
        gentle_gradient_max_x = radius * math.cos(math.radians(30))
        gentle_gradient_max_y = (
            radius ** 2 - gentle_gradient_max_x ** 2) ** 0.5

        for max_x, max_y in (
            (steep_gradient_max_x, steep_gradient_max_y),
            (gentle_gradient_max_x, gentle_gradient_max_y)
        ):
            for x_op, y_op in itertools.product("+-", repeat=2):
                if x_op == "+":
                    x1 = centx + 100/radius * max_x,
                    x2 = centx + 120/radius * max_x
                else:
                    x1 = centx - 100/radius * max_x
                    x2 = centx - 120/radius * max_x
                if y_op == "+":
                    y1 = centy + 100/radius * max_y
                    y2 = centy + 120/radius * max_y
                else:
                    y1 = centy - 100/radius * max_y
                    y2 = centy - 120/radius * max_y

                # White if passed.
                if (
                    max_x == steep_gradient_max_x and x_op == "+" and
                    (
                        (y_op == "-" and angle > 30) or
                        (y_op == "+" and angle > 150))
                ) or (
                    max_x == gentle_gradient_max_x and x_op == "+" and
                    (
                        (y_op == "-" and angle > 60) or
                        (y_op == "+" and angle > 120))
                ): 
                    self.create_line(x1, y1, x2, y2, fill=WHITE)
                else:
                    self.create_line(x1, y1, x2, y2, fill=BLACK)
        
        # Creates the countdown pointer.
        if angle == 0:
            self.create_polygon(
                centx - 10, centy, centx + 10, centy, centx, 0, fill=GREY)
        elif angle == 90:
            self.create_polygon(
                centx, centy - 10, centx, centy + 10, centx + radius, centy,
                fill=GREY)
        elif angle == 180:
            self.create_polygon(
                centx - 10, centy, centx + 10, centy, centx, centy + radius,
                fill=GREY)
        else:
            if angle < 90:
                x_shift = 10 * math.cos(math.radians(angle))
                y_shift = (10 ** 2 - x_shift ** 2) ** 0.5

                x_right = radius * math.cos(math.radians(90 - angle))
                y_up = (radius ** 2 - x_right ** 2) ** 0.5

                self.create_polygon(
                    centx - x_shift, centy - y_shift,
                    centx + x_shift, centy + y_shift,
                    centx + x_right, centy - y_up, fill=GREY)
            else:
                x_shift = 10 * math.sin(math.radians(angle - 90))
                y_shift = (100 - x_shift ** 2) ** 0.5

                x_right = radius * math.cos(math.radians(angle - 90))
                y_down = (radius ** 2 - x_right ** 2) ** 0.5

                self.create_polygon(
                    centx + x_shift, centy - y_shift,
                    centx - x_shift, centy + y_shift,
                    centx + x_right, centy + y_down, fill=GREY)


class EnterSolutionFrame(tk.Frame):
    """
    Where the player enters a solution with their selected numbers
    for their given number.
    """

    def __init__(self, master: Game, numbers: list[int], target: int) -> None:
        super().__init__(master)
        self.master = master
        self.numbers = numbers
        self.target = target

        self.title_label = tk.Label(
            self, font=ink_free(50, True), text="Enter your best solution!")
        self.solution_label = SolutionLabel(self)
        self.solution_buttons = SolutionButtonsFrame(self)
        self.option_buttons = EnterSolutionOptionsFrame(self)

        self.used_numbers = []
        self.opening_parentheses = 0
        self.closing_parentheses = 0

        self.title_label.pack(padx=25, pady=15)
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
            new_solution = current_solution + "x" + to_add
        else:
            if len(current_solution) >= MAX_SOLUTION_LENGTH - len(to_add) + 1:
                # Cannot insert n more characters.
                return
            new_solution = current_solution + to_add

        self.solution_label.config(text=new_solution)

        if to_add.isdigit() or to_add == ")":
            # Next, an operator or parenthesis is expected.
            for button in self.solution_buttons:
                button.config(
                    state=(
                    "disabled" if button.cget("text").isdigit()
                    else "normal"))
        else:
            # Next, a number or closing parenthesis is expected.
            for button in self.solution_buttons:
                button.config(
                    state=(
                    "normal" if button.cget("text").isdigit()
                    or button.cget("text") == "(" else "disabled"))
        
        if to_add.isdigit() and not from_pop:
            self.used_numbers.append(to_add)
        
        for number in self.used_numbers:
            for button in self.solution_buttons:
                # Disables used numbers in grey instead of red.
                if (
                    button.cget("text") == number
                    and (
                        button.cget("disabledforeground") != GREY
                        or button.cget("state") == "normal")
                ):
                    button.config(state="disabled", disabledforeground=GREY)
                    break
        
        # Disable all except closing parenthesis or remove last input.
        if len(self.used_numbers) == NUMBER_COUNT:
            for button in self.solution_buttons:
                button.config(
                    state="disabled" if button.cget("text") not in ")←"
                    else "normal")
        
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
            state=(
                "normal" if
                self.opening_parentheses == self.closing_parentheses
                and (to_add.isdigit() or to_add == ")") else "disabled"))
    
    def pop(self) -> None:
        """
        Removes the previous input from the solution.
        """
        # Gets last input: either a number, operator or parenthesis.
        current_solution = self.solution_label.get()
        if not current_solution:
            return

        index = -1
        while current_solution[index:].isdigit():
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
                    button.config(state="normal", disabledforeground=RED)
                    break
        elif to_remove == "(":
            self.opening_parentheses -= 1
        elif to_remove == ")":
            self.closing_parentheses -= 1

        new_solution = current_solution[:index]

        if not new_solution:
            self.reset()
            return

        # Re-adds input before the removed input.
        # This prevents code duplication.
        index = -1
        while new_solution[index:].isdigit():
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
                state=(
                    "normal" if button.cget("text").isdigit()
                    or button.cget("text") == "(" else "disabled"),
                disabledforeground=RED)

        self.option_buttons.reset_button.config(state="disabled")
        self.option_buttons.submit_button.config(state="disabled")
    
    def enter_key(self, event: tk.Event) -> None:
        """
        Takes a key which represents an operator or parenthesis,
        and if the corresponding button is enabled, the code which
        the corresponding runs will run by the keybind.
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
        to_evaluate = solution.replace("x", "*").replace("÷", "/")
        INCORRECT_SOLUTION_SFX.stop()

        try:
            is_correct = round(eval(to_evaluate), 10) == self.target
        except ZeroDivisionError:
            messagebox.showerror(
                "Cannot divide by 0",
                    "Your solution is invalid because you are trying to "
                    "divide by 0, but this is undefined.")
            return

        if is_correct:
            CORRECT_SOLUTION_SFX.play()
            self.master.proceed_to_finish(solution, self.target)
        else:
            INCORRECT_SOLUTION_SFX.play()
        
    def skip(self) -> None:
        """
        If the player has no solution, they can skip solution entry.
        This will be counted as a loss.
        """
        self.master.proceed_to_finish(None, self.target)


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
        
        row_2 = [SolutionInputButton(self, operator) for operator in "+-x÷()"]
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
            bg=ORANGE, activebackground=RED,
            command=master.skip)
        
        self.reset_button.pack(padx=10, side="left")
        self.submit_button.pack(padx=10, side="left")
        self.skip_button.pack(padx=10, side="right")