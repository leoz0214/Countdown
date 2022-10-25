"""
Achievements serve as motivation for the player to
replay the game, adding engagement.
"""
import tkinter as tk
from typing import Literal

import menu
from colours import *
from utils import ink_free


def format_achievement(
    name: str, description: str,
    tier: Literal["bronze", "silver", "gold", "platinum"]) -> str:
    """
    Formats an achievement to be displayed to the player if earned.
    """
    return "{} - {} ({}) ✓".format(name, description, tier)


def format_special_achievement(key: str) -> str:
    """
    Format a special achievement.
    """
    return format_achievement(
        SPECIAL_ACHIEVEMENTS[key]["name"],
        SPECIAL_ACHIEVEMENTS[key]["description"], 
        SPECIAL_ACHIEVEMENTS[key]["tier"])


def create_special_achievement(
    name: str, description: str,
    tier: Literal["bronze", "silver", "gold", "platinum"]) -> dict[str, str]:
    """
    Returns a dictionary for a special achievement.
    """
    return {
        "name": name,
        "description": description,
        "tier": tier
    }


# One-time achievements.
SPECIAL_ACHIEVEMENTS = {
    "obsession": create_special_achievement(
        "Obsession!", "Play 40 games in the span of 24 hours.", "silver"),

    "addiction": create_special_achievement(
        "Addiction!", "Play 250 games in the span of 7 days.", "gold"),

    "incorrect_solution": create_special_achievement(
        "OOPS!", "Submit an incorrect solution", "bronze"),

    "small_numbers": create_special_achievement(
        "Small numbers reign!",
        "Find a solution using exactly 5 small numbers and 0 big numbers",
        "gold"),

    "big_numbers": create_special_achievement(
        "Brutal big numbers!",
        "Find a solution using exactly 5 big numbers and 0 small numbers",
        "gold"),

    "all_numbers": create_special_achievement(
        "Full House!",
        "Find a solution using all the numbers provided", "silver"),

    "all_operators": create_special_achievement(
        "Together they are strong!",
        "Use all operators in a solution", "silver"),

    "one_operator": create_special_achievement(
        "One Operator!", "Find a solution using only one operator", "gold")
}


class AchievementsWindow(tk.Frame):
    """
    Holds the achievements user interface.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root
        self.root.title("Countdown - Achievements")

        self.title_label = tk.Label(
            self, font=ink_free(75, True), text="Achievements")
        
        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=self.back)
        
        self.title_label.pack(padx=10, pady=10)
        self.back_button.pack(padx=10, pady=10)
    
    def back(self) -> None:
        """
        Returns back to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()