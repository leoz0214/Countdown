"""
Allows the player to customise their experience with settings, and also
to reset all data (comes with a stark warning and confirmation).
"""
import tkinter as tk
from tkinter import messagebox
import math

import menu
import widgets
import data
from utils import ink_free, get_music
from colours import *


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
    "Flight of the Bumblebee": "flightofbumblebee.wav"
}

COUNTDOWN_MUSIC = {
    file: get_music(file) for file in COUNTDOWN_MUSIC_NAME_TO_FILE.values()
}


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

        self.title_label.pack(padx=10, pady=5)
        self.pages_frame.pack(padx=10, pady=5)
        self.navigation_frame.pack(padx=10, pady=5)
    
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
        data.set_options(new_options)
        messagebox.showinfo("Success", "Successfully saved options.")
    
    def reset_options(self) -> None:
        """
        Resets options to default, upon confirmation.
        """
        if messagebox.askyesnocancel(
            "Confirm reset options",
                "Are you sure you would like to reset the options?"
        ):
            data.set_options(DEFAULT_OPTIONS)
            self.destroy()
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
                data.get_options()[key]["on"]
                if isinstance(DEFAULT_OPTIONS[key], dict)
                else data.get_options()[key]))

        self.name_label = tk.Label(
            self, font=ink_free(25), text=name)
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
            value=data.get_options()["music"]["countdown"])
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

        self.radiobuttons = [
            tk.Radiobutton(
                self, font=ink_free(12), text=name,
                variable=self.master.countdown, value=file, width=20,
                border=3, bg=ORANGE, activebackground=GREEN,
                selectcolor=GREEN, indicatoron=False, command=self.play)
            for name, file in COUNTDOWN_MUSIC_NAME_TO_FILE.items()]
        # n x 2 grid of radiobuttons representing music tracks
        for i, radiobutton in enumerate(self.radiobuttons):
            radiobutton.grid(row=i//2, column=i % 2, padx=5, pady=5)
        
        self.stop_button = tk.Button(
            self, font=ink_free(15), text="Stop playback", width=15, border=5,
            bg=ORANGE, activebackground=RED, command=self.stop)
        self.stop_button.grid(
            row=math.ceil(len(self.radiobuttons) / 2), column=0,
            columnspan=2, padx=5, pady=5)
    
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
            value=data.get_options()["auto_generate"]["min_small"])
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
            from_=2, to=5, orient="horizontal", length=200, sliderlength=50,
            command=lambda _: self.update_max_big_number_count())

        self.max_big_numbers_label = tk.Label(
            self, font=ink_free(15), text="Maximum big numbers")
        self.max_big_numbers_scale = tk.Scale(
            self, font=ink_free(15), variable=self.master.max_big_numbers,
            from_=2, to=5, orient="horizontal", length=200, sliderlength=50,
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
            value=data.get_options()["solution_time_limit"]["minutes"])
        
        self.minutes_scale = tk.Scale(
            self, font=ink_free(15), variable=self.minutes, from_=1, to=5,
            orient="horizontal", length=200, sliderlength=40)
        if not self.is_on():
            self.minutes_scale.config(state="disabled")
        self.minutes_scale.grid(row=1, column=0, columnspan=3, padx=5, pady=5)


class OptionsPagesFrame(widgets.PagesFrame):
    """
    Holds the various options, displayed on different pages.
    """

    def __init__(self, master: OptionsWindow) -> None:
        super().__init__(master, 1, PAGE_COUNT, 1200, 420)

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