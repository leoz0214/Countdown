"""
Allows the player to customise their experience with settings, and also
to reset all data (comes with a stark warning and confirmation).
"""
import json
import math
import tkinter as tk
from tkinter import messagebox
from typing import Any

import menu
from utils import widgets
from utils.colours import *
from utils.io import check_folder_exists, FOLDER, reset_data
from utils.utils import ink_free, get_music, bool_to_state


PAGE_COUNT = 4

DEFAULT_OPTIONS = {
    "music": {"on": True, "countdown": "countdown.wav"},
    "sfx": True,
    "stats": True,
    "auto_generate": {"on": False, "min_small": 4},
    "solution_time_limit": {"on": False, "minutes": 2}
}

COUNTDOWN_MUSIC_NAME_TO_FILE = {
    "Countdown": "countdown.wav",
    "Flight of the Bumblebee": "flightofbumblebee.wav",
    "Can Can": "cancan.wav",
    "8-bit": "8bit.wav",
    "Relax": "relax.wav"
}

COUNTDOWN_MUSIC = {
    file: get_music(file) for file in COUNTDOWN_MUSIC_NAME_TO_FILE.values()
}

MIN_MIN_SMALL = 2
MAX_MIN_SMALL = 5

MIN_SOLUTION_ENTRY_MINUTES = 1
MAX_SOLUTION_ENTRY_MINUTES = 5

RESET_DATA_CONFIRMATION_TEXT = "Yes, I am sure I want to reset"

OPTIONS_FILE = f"{FOLDER}/options.json"


def options_dict_is_valid(options: dict, expected: dict) -> bool:
    """
    Checks if the options dict (or any nested ones) is as expected
    (same keys in the correct order, same value types).
    """
    if len(options) != len(expected):
        return False
    for key, expected_key in zip(options, expected):
        if (
            (key != expected_key) or
            # Invalid music file.
            (key == "countdown" and options[key] not in COUNTDOWN_MUSIC) or
            (key == "min_small"
                and not MIN_MIN_SMALL <= options[key] <= MAX_MIN_SMALL) or
            (key == "minutes"
                and not MIN_SOLUTION_ENTRY_MINUTES
                <= options[key] <= MAX_SOLUTION_ENTRY_MINUTES)
        ):
            return False
    for value, default_value in zip(options.values(), expected.values()):
        if type(value) is not type(default_value):
            return False
        if isinstance(value, dict):
            # Recursively checks nested dicts are also valid.
            if not options_dict_is_valid(value, default_value):
                return False
    return True


@check_folder_exists()
def get_options() -> dict:
    """
    Returns the player's settings.
    """
    try:
        with open(OPTIONS_FILE, "r", encoding="utf8") as f:
            options = json.load(f)
        if not options_dict_is_valid(options, DEFAULT_OPTIONS):
            raise ValueError
        return options
    except (FileNotFoundError, ValueError):
        # File does not exist or is corrupt. (Re)set settings to default.
        set_options(DEFAULT_OPTIONS)
        return DEFAULT_OPTIONS


def get_option(*keys: str) -> Any:
    """
    Retrieves an option by dictionary keys.
    """
    option = get_options()
    for key in keys:
        option = option[key]
    return option


@check_folder_exists()
def set_options(options: dict) -> None:
    """
    Updates the player's settings.
    """
    with open(OPTIONS_FILE, "w", encoding="utf8") as f:
        json.dump(options, f)


class OptionsWindow(tk.Frame):
    """
    Holds the options GUI.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Options")

        self.title_label = tk.Label(
            self, font=ink_free(50, True), text="Options")
        self.pages_frame = OptionsPagesFrame(self)
        self.navigation_frame = OptionsNavigationFrame(self)

        self.title_label.pack(padx=10)
        self.pages_frame.pack(padx=10)
        self.navigation_frame.pack(padx=10)

    def back(self) -> None:
        """
        Returns back to the main menu.
        """
        self.destroy()
        # Stops the current playback music demo (if playing)
        music = (
            self.pages_frame.music_frame.countdown_music_frame.current_music)
        if music is not None:
            music.stop()
        menu.MainMenu(self.root).pack()

    def save_options(self) -> None:
        """
        Saves the settings currently specified.
        """
        new_options = {
            "music": {
                "on": self.pages_frame.music_frame.is_on(),
                "countdown": self.pages_frame.music_frame.countdown.get()
            },
            "sfx": self.pages_frame.sfx_frame.is_on(),
            "stats": self.pages_frame.stats_frame.is_on(),
            "auto_generate": {
                "on": self.pages_frame.auto_generate_frame.is_on(),
                "min_small": (
                    self.pages_frame.auto_generate_frame
                    .min_small_numbers.get())
            },
            "solution_time_limit": {
                "on": self.pages_frame.solution_time_limit_frame.is_on(),
                "minutes": (
                    self.pages_frame.solution_time_limit_frame.minutes.get())
            }
        }
        set_options(new_options)
        music = (
            self.pages_frame.music_frame.countdown_music_frame.current_music)
        if music is not None:
            music.stop()
        messagebox.showinfo("Success", "Successfully saved options.")

    def reset_options(self) -> None:
        """
        Resets options to default, upon confirmation.
        """
        if messagebox.askyesnocancel(
            "Confirm reset options",
                "Are you sure you would like to reset the options?"
        ):
            set_options(DEFAULT_OPTIONS)
            self.destroy()
            music = (
                self.pages_frame.
                music_frame.countdown_music_frame.current_music)
            if music is not None:
                music.stop()
            OptionsWindow(self.root).pack()
            messagebox.showinfo("Success", "Successfully reset options.")


class StateOptionFrame(tk.Frame):
    """
    Holds a setting which can either be ON or OFF.
    This setting is stored as a boolean.
    """

    def __init__(self, master: tk.Frame, name: str, key: str) -> None:
        super().__init__(master)
        self.key = key
        self.on = tk.BooleanVar(
            value=(
                get_option(key, "on") if isinstance(DEFAULT_OPTIONS[key], dict)
                else get_option(key)))

        self.name_label = tk.Label(self, font=ink_free(25), text=name)
        self.on_radiobutton = tk.Radiobutton(
            self, font=ink_free(20), text="ON", width=4, border=5,
            variable=self.on, value=True, bg=GREY, activebackground=GREEN,
            selectcolor=GREEN, indicatoron=False)
        self.off_radiobutton = tk.Radiobutton(
            self, font=ink_free(20), text="OFF", width=4, border=5,
            variable=self.on, value=False, bg=GREY, activebackground=RED,
            selectcolor=RED, indicatoron=False)

        self.name_label.grid(row=0, column=0, padx=25, pady=10)
        self.on_radiobutton.grid(row=0, column=1, padx=5, pady=10, sticky="e")
        self.off_radiobutton.grid(
            row=0, column=2, padx=5, pady=10, sticky="w")

    def is_on(self) -> bool:
        """
        Returns the current state of the setting.
        """
        return self.on.get()


class MusicFrame(StateOptionFrame):
    """
    Handles the music setting - whether it is on or off and
    which music to play for the countdown.
    """

    def __init__(self, master: tk.Frame) -> None:
        super().__init__(master, "Music", "music")
        self.on_radiobutton.config(command=self.enable)
        self.off_radiobutton.config(command=self.disable)

        self.countdown = tk.StringVar(
            value=get_option("music", "countdown"))
        self.countdown_music_frame = CountdownMusicLabelFrame(self)
        if not self.is_on():
            self.disable()
        self.countdown_music_frame.grid(
            row=1, column=0, columnspan=3, padx=5, pady=5)

    def enable(self) -> None:
        """
        Allows access to the countdown music setting.
        """
        for widget in self.countdown_music_frame.children.values():
            widget.config(state="normal")

    def disable(self) -> None:
        """
        Stops access to the countdown music setting.
        """
        for widget in self.countdown_music_frame.children.values():
            widget.config(state="disabled")
        self.countdown_music_frame.stop()


class CountdownMusicLabelFrame(tk.LabelFrame):
    """
    Allows the player to choose which music to play for the
    countdown, also allowing a sample of each track.
    """

    def __init__(self, master: MusicFrame) -> None:
        super().__init__(
            master, font=ink_free(15),
            text="Countdown Music", labelanchor="n")
        self.master = master
        self.current_music = None

        self.radiobuttons = (
            tk.Radiobutton(
                self, font=ink_free(12), text=name,
                variable=self.master.countdown, value=file, width=20,
                border=3, bg=ORANGE, activebackground=GREEN,
                selectcolor=GREEN, indicatoron=False, command=self.play)
            for name, file in COUNTDOWN_MUSIC_NAME_TO_FILE.items())
        # n x 5 grid of radiobuttons representing music tracks
        for i, radiobutton in enumerate(self.radiobuttons):
            radiobutton.grid(row=i // 5, column=i % 5, padx=5, pady=5)

        self.stop_button = tk.Button(
            self, font=ink_free(15), text="Stop playback", width=15, border=5,
            bg=ORANGE, activebackground=RED, command=self.stop)
        self.stop_button.grid(
            row=math.ceil((i + 1) / 5), column=0,
            columnspan=5, padx=5, pady=5)

    def play(self) -> None:
        """
        Plays current selection.
        """
        self.stop()
        self.current_music = COUNTDOWN_MUSIC[self.master.countdown.get()]
        self.current_music.play()

    def stop(self) -> None:
        """
        Stops current selection.
        """
        if self.current_music is not None:
            self.current_music.stop()
            self.current_music = None


class AutoGenerateFrame(StateOptionFrame):
    """
    Allows the player to automatically generate numbers to use
    upon entering a round.
    """

    def __init__(self, master: tk.Frame) -> None:
        super().__init__(master, "Auto generate 7 numbers", "auto_generate")
        self.on_radiobutton.config(command=self.enable)
        self.off_radiobutton.config(command=self.disable)

        self.min_small_numbers = tk.IntVar(
            value=get_option("auto_generate", "min_small"))
        self.max_big_numbers = tk.IntVar(value=7 - self.min_small_numbers.get())
        self.number_counts_frame = AutoGenerateNumberCountsFrame(self)
        if not self.is_on():
            self.disable()
        self.number_counts_frame.grid(
            row=1, column=0, columnspan=3, padx=5, pady=5)

    def enable(self) -> None:
        """
        Allows number counts to be changed.
        """
        for widget in self.number_counts_frame.children.values():
            widget.config(state="normal")

    def disable(self) -> None:
        """
        Disallows number counts to be changed.
        """
        for widget in self.number_counts_frame.children.values():
            widget.config(state="disabled")


class AutoGenerateNumberCountsFrame(tk.Frame):
    """
    Linked with auto generation to decide the maximum number
    of small/big numbers to be randomly selected.
    """

    def __init__(self, master: AutoGenerateFrame) -> None:
        super().__init__(master)
        self.master = master

        self.min_small_numbers_label = tk.Label(
            self, font=ink_free(15), text="Minimum small numbers")
        self.min_small_numbers_scale = tk.Scale(
            self, font=ink_free(15), variable=self.master.min_small_numbers,
            from_=MIN_MIN_SMALL, to=MAX_MIN_SMALL, orient="horizontal",
            length=200, sliderlength=50,
            command=lambda _: self.update_max_big_number_count())

        self.max_big_numbers_label = tk.Label(
            self, font=ink_free(15), text="Maximum big numbers")
        self.max_big_numbers_scale = tk.Scale(
            self, font=ink_free(15), variable=self.master.max_big_numbers,
            from_=7 - MAX_MIN_SMALL, to=7 - MIN_MIN_SMALL,
            orient="horizontal", length=200, sliderlength=50,
            command=lambda _: self.update_min_small_number_count())

        self.min_small_numbers_label.grid(row=0, column=0, padx=5, pady=5)
        self.min_small_numbers_scale.grid(row=0, column=1, padx=5, pady=5)
        self.max_big_numbers_label.grid(row=1, column=0, padx=5, pady=5)
        self.max_big_numbers_scale.grid(row=1, column=1, padx=5, pady=5)

    def update_min_small_number_count(self) -> None:
        """
        Updates the minimum number of small numbers allowed.
        """
        self.master.min_small_numbers.set(
            7 - self.master.max_big_numbers.get())

    def update_max_big_number_count(self) -> None:
        """
        Updates the maximum number of big numbers allowed.
        """
        self.master.max_big_numbers.set(
            7 - self.master.min_small_numbers.get())


class SolutionTimeLimitFrame(StateOptionFrame):
    """
    Allows the player to set a maximum time window to enter a solution.
    """

    def __init__(self, master: tk.Frame) -> None:
        super().__init__(
            master, "Time limit to enter solution (minutes)",
            "solution_time_limit")
        self.on_radiobutton.config(
            command=lambda: self.minutes_scale.config(state="normal"))
        self.off_radiobutton.config(
            command=lambda: self.minutes_scale.config(state="disabled"))
        self.minutes = tk.IntVar(
            value=get_option("solution_time_limit", "minutes"))

        self.minutes_scale = tk.Scale(
            self, font=ink_free(15), variable=self.minutes,
            from_=MIN_SOLUTION_ENTRY_MINUTES, to=MAX_SOLUTION_ENTRY_MINUTES,
            orient="horizontal", length=200, sliderlength=40,
            state=bool_to_state(self.is_on()))
        self.minutes_scale.grid(row=1, column=0, columnspan=3, padx=5, pady=5)


class ResetDataFrame(tk.Frame):
    """
    Where the player has the option to reset all of their in-game data,
    with a confirmation.
    """

    def __init__(self, master: tk.Frame) -> None:
        super().__init__(master)
        self.master = master
        self.title_label = tk.Label(
            self, font=ink_free(25, True), text="Reset Data", fg=RED)
        self.description_label = tk.Label(
            self, font=ink_free(15),
            text=(
                "All of your in-game data will be reset and  "
                "you will start from scratch.\n"
                "To ensure you are certain about this, please type: "
                f"{RESET_DATA_CONFIRMATION_TEXT}"), fg=RED)
        self.confirmation_entry = tk.Entry(self, font=ink_free(15), width=35)
        self.reset_button = tk.Button(
            self, font=ink_free(15), text="Reset", width=10, border=3,
            bg=ORANGE, activebackground=RED, command=self.reset)

        self.title_label.pack(padx=10, pady=10)
        self.description_label.pack(padx=10, pady=10)
        self.confirmation_entry.pack(padx=10, pady=10)
        self.reset_button.pack(padx=10, pady=10)

    def reset(self) -> None:
        """
        Upon confirmation, resets all player data.
        """
        text = self.confirmation_entry.get()
        if not text:
            messagebox.showerror(
                "No confirmation", "Please enter the confirmation text.")
        elif text != RESET_DATA_CONFIRMATION_TEXT:
            messagebox.showerror(
                "Incorrect confirmation",
                    "You did not enter the confirmation text correctly. "
                    "It must be exactly the same.")
        elif messagebox.askyesnocancel(
            "Final confirmation",
                "This is your last chance to preserve your current data.\n"
                "Are you 100% sure that this is what you want?\n"
                "Your data cannot be restored once it is wiped.\n",
            icon="warning"
        ):
            reset_data()
            self.master.master.back()
            messagebox.showinfo("Success", "Clean slate!")


class OptionsPagesFrame(widgets.PagesFrame):
    """
    Holds the various options, displayed on different pages.
    """

    def __init__(self, master: OptionsWindow) -> None:
        super().__init__(master, 1, PAGE_COUNT, 1200, 450)
        self.master = master

        page_1 = tk.Frame(self)
        self.music_frame = MusicFrame(page_1)
        self.sfx_frame = StateOptionFrame(page_1, "Sound Effects", "sfx")
        self.music_frame.pack()
        self.sfx_frame.pack()
        self.add(page_1)

        page_2 = tk.Frame(self)
        self.stats_frame =  StateOptionFrame(
            page_2, "Stats/Achievements/History", "stats")
        self.auto_generate_frame = AutoGenerateFrame(page_2)
        self.stats_frame.pack()
        self.auto_generate_frame.pack()
        self.add(page_2)

        self.solution_time_limit_frame = SolutionTimeLimitFrame(self)
        self.add(self.solution_time_limit_frame)

        self.reset_data_frame = ResetDataFrame(self)
        self.add(self.reset_data_frame)

        self.show()


class OptionsNavigationFrame(tk.Frame):
    """
    Buttons to control certain events of the options window.
    """

    def __init__(self, master: OptionsWindow) -> None:
        super().__init__(master)
        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=master.back)
        self.save_button = tk.Button(
            self, font=ink_free(25), text="Save", width=10, border=5,
            bg=ORANGE, activebackground=GREEN, command=master.save_options)
        self.reset_button = tk.Button(
            self, font=ink_free(25), text="Reset", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=master.reset_options)

        self.back_button.pack(padx=10, pady=5, side="left")
        self.save_button.pack(padx=10, pady=5, side="left")
        self.reset_button.pack(padx=10, pady=5)
