import tkinter as tk
import secrets

import menu
from colours import *
from font import ink_free


NUMBER_COUNT = 7
MAX_SMALL_COUNT = MAX_BIG_COUNT = 6


class Game(tk.Frame):
    """
    Holds the actual countdown game.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Game")

        self.select_numbers_frame = SelectNumbersFrame(self)
        self.select_numbers_frame.pack()
    
    def home(self) -> None:
        """
        Return back to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()


class SelectNumbersFrame(tk.Frame):
    """
    Allows the play to select numbers to be used, either:
    - Big (25, 50, 75, 100)
    - Small (1-9)

    Minimum one of each, total 7.
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
        self.selected_numbers_frame.selected_numbers[count].config(
            text=number)
        self.selected_numbers_frame.count += 1

        if self.selected_numbers_frame.count == NUMBER_COUNT:
            # Ready to begin - all numbers selected.
            self.small_numbers_frame.destroy()
            self.big_numbers_frame.destroy()
            self.navigation_frame.start_button.config(state="normal")


class SelectedNumbersFrame(tk.Frame):
    """
    Holds the 7 numbers which are selected randomly.
    """

    def __init__(self, master: SelectNumbersFrame) -> None:
        super().__init__(master)
        self.count = 0
        self.selected_numbers = [
            tk.Label(
                self, font=ink_free(50), width=4, height=1,
                highlightbackground=BLACK, highlightthickness=3)
            for _ in range(NUMBER_COUNT)]
        
        for box in self.selected_numbers:
            box.pack(padx=5, side="left")


class SmallNumbersFrame(tk.Frame):
    """
    Holds the 6 small numbers which can be selected.
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
    Holds the 6 big numbers which can be selected.
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
            state="disabled")
        
        self.back_button.pack(padx=10, side="left")
        self.start_button.pack(padx=10, side="right")