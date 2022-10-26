"""
Achievements serve as motivation for the player to
replay the game, adding engagement.
"""
import tkinter as tk
from typing import Callable, Literal
from collections import namedtuple

import menu
import level
import data
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

    
def create_tiered_achievement(
    name: str, function: Callable,
    requirements: tuple, descriptions: list[str]) -> dict:
    """
    Returns a dictionary for a tiered achievement.
    """
    return {
        "name": name,
        "function": function,
        "requirements": requirements,
        "descriptions": descriptions
    }


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


def get_tiered_achievement_descriptions(
    format_string: str, tier_requirements: "AchievementTierRequirements"
) -> "AchievementTierDescriptions":
    """
    Gets tiered achievement descriptions based on requirements for each
    tier and a format string to put the number for each tier into.
    """
    return AchievementTierDescriptions(
        *(
            format_string.format(value)
            for value in (
                tier_requirements.bronze, tier_requirements.silver,
                tier_requirements.gold, tier_requirements.platinum)))


def get_achievement_count() -> int:
    """
    Returns the number of achievements earned by the player.
    """
    return -1 # To do


AchievementTierRequirements = namedtuple(
    "AchievementTierRequirements", "bronze silver gold platinum")

AchievementTierDescriptions = namedtuple(
    "AchievementTierDescriptions", "bronze silver gold platinum")


# Tiered achievements
TIERED_ACHIEVEMENTS = {
    "games_played": create_tiered_achievement(
        "Countdown Commitment", data.get_games_played,
        (requirements := AchievementTierRequirements(10, 50, 250, 2500)),
        get_tiered_achievement_descriptions("Play {} games", requirements)),
    
    "wins": create_tiered_achievement(
        "Getting good at maths!", data.get_win_count,
        (requirements := AchievementTierRequirements(5, 25, 125, 1000)),
        get_tiered_achievement_descriptions("Win {} games", requirements)),
    
    "time_played": create_tiered_achievement(
        "Time flies when you're having fun", data.get_seconds_played,
        # In seconds played.
        AchievementTierRequirements(1200, 7200, 36000, 180000),
        AchievementTierDescriptions(
            *(
                "Play {}".format(duration) for duration in (
                    "20 minutes", "2 hours", "10 hours", "50 hours")))),
    
    "level": create_tiered_achievement(
        "Expertise Developement", data.get_total_xp,
        # By XP
        AchievementTierRequirements(
            *(level.get_total_xp_for_level(lvl) for lvl in (5, 12, 25, 75))),
        AchievementTierDescriptions(
            *("Reach level {}".format(lvl) for lvl in (5, 12, 25, 75)))),
    
    "best_streak": create_tiered_achievement(
        "Winner Winner Chicken Dinner", data.get_best_win_streak,
        (requirements := AchievementTierRequirements(2, 5, 20, 78)),
        get_tiered_achievement_descriptions(
            "Reach a win streak of {}", requirements)),
    
    "achievements": create_tiered_achievement(
        "To first earn this achievement, you must earn achievements",
        get_achievement_count,
        (requirements := AchievementTierRequirements(7, 14, 21, 28)),
        get_tiered_achievement_descriptions(
            "Earn {} achievements", requirements))
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