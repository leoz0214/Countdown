import tkinter as tk
import secrets

from pygame import mixer

import menu
import generate
from colours import *
from font import ink_free


mixer.init()

NUMBER_COUNT = 7
MAX_SMALL_COUNT = MAX_BIG_COUNT = 5

COUNT_SFX = mixer.Sound("./audio/count.wav")
GO_SFX = mixer.Sound("./audio/go.wav")
COUNTDOWN_MUSIC = mixer.Sound("./audio/countdown.wav")

SHUFFLES_BEFORE_REAL_NUMBER = 25
SHUFFLE_DELAY_MS = 50


def draw_circle(
    canvas: tk.Canvas, x: int, y: int, radius: int,
    fill: str | None = None) -> None:
    """
    Draws a circle with a given centre and radius onto the canvas.
    """
    canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius, fill=fill)


class Game(tk.Frame):
    """
    Holds the actual countdown game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Game")

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
        self.after(1000, lambda: self.pre_countdown(seconds-1))
    
    def start(self) -> None:
        """
        Begins the countdown round.
        """
        self.pre_countdown_label.destroy()
        GO_SFX.stop()
        target_number = generate.generate_number(self.numbers)

        self.target_number_label = TargetNumberLabel(self, target_number)
        self.selected_numbers_frame = SelectedNumbersFrame(self, self.numbers)

        self.target_number_label.pack(padx=25, pady=15)
        self.selected_numbers_frame.pack(padx=10, pady=10)

        self.target_number_label.shuffle_number_display(
            SHUFFLES_BEFORE_REAL_NUMBER)
    
    def count_down(self) -> None:
        """
        Starts the 30 second timer.
        """
        CountdownClock(self).pack(padx=10, pady=10)
        COUNTDOWN_MUSIC.play()


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
            self.master.count_down()


class CountdownClock(tk.Canvas):
    """
    Displays the time remaining for the player to form a solution
    before automatically being directed to enter a solution.
    """

    def __init__(self, master: CountdownFrame) -> None:
        super().__init__(master, width=250, height=250)
        draw_circle(self, 125, 125, 123, SILVER)
        self.create_line(125, 0, 125, 250, fill=BLACK)
        self.create_line(0, 125, 250, 125, fill=BLACK)
        draw_circle(self, 125, 125, 10, GREY)

