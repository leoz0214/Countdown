"""
Achievements serve as motivation for the player to
replay the game, enhancing engagement of the player.
"""
import json
import tkinter as tk
from collections import namedtuple
from typing import Callable, Literal

import menu
from utils import widgets
from utils.colours import *
from utils.io import check_folder_exists, FOLDER
from utils.utils import ink_free, seconds_to_hhmmss
from . import level
from . import stats


PAGE_COUNT = 4
TIERS = ("bronze", "silver", "gold", "platinum")

SPECIAL_ACHIEVEMENTS_FILE = f"{FOLDER}/achievements.json"


AchievementTierRequirements = namedtuple(
    "AchievementTierRequirements", " ".join(TIERS))

AchievementTierDescriptions = namedtuple(
    "AchievementTierDescriptions", " ".join(TIERS))


def valid_special_achievements(achievements: dict[str, bool]) -> bool:
    """
    Returns True if the special achievements data is valid, else False.
    """
    return (
        isinstance(achievements, dict)
        and len(achievements) == len(SPECIAL_ACHIEVEMENTS)
        and all(
            actual_key == expected_key
            and isinstance(achievements[actual_key], bool)
                for actual_key, expected_key in zip(
                    achievements, SPECIAL_ACHIEVEMENTS)))


@check_folder_exists()
def get_special_achievements() -> dict[str, bool]:
    """
    Gets the status of special achievements.
    True indicates a special achievement is complete, else False.
    """
    try:
        with open(SPECIAL_ACHIEVEMENTS_FILE, "r", encoding="utf8") as f:
            special_achievements = json.load(f)
        if not valid_special_achievements(special_achievements):
            raise ValueError
        return special_achievements
    except (FileNotFoundError, ValueError):
        # (Re)set all special achievements to unachieved.
        special_achievements = dict.fromkeys(SPECIAL_ACHIEVEMENTS, False)
        with open(SPECIAL_ACHIEVEMENTS_FILE, "w", encoding="utf8") as f:
            json.dump(special_achievements, f)
        return special_achievements


def get_special_achievement(key: str) -> bool:
    """
    Returns the status of a special achievement (True if complete).
    """
    return get_special_achievements()[key]


@check_folder_exists()
def complete_special_achievement(key: str) -> bool:
    """
    Sets a special achievement to True if not already.
    Returns True if the change was made, else False.
    """
    special_achievements = get_special_achievements()
    if special_achievements[key]:
        return False
    special_achievements[key] = True
    with open(SPECIAL_ACHIEVEMENTS_FILE, "w", encoding="utf8") as f:
        json.dump(special_achievements, f)
    return True


def format_achievement(
    name: str, description: str,
    tier: Literal["bronze", "silver", "gold", "platinum"]) -> str:
    """
    Formats an achievement to be displayed to the player if earned.
    """
    return f"{name} - {description} ({tier}) ✓"


def format_tiered_achievement(key: str, index: int) -> str:
    """
    Formats a tiered achievement.
    """
    return format_achievement(
        TIERED_ACHIEVEMENTS[key]["name"],
        TIERED_ACHIEVEMENTS[key]["descriptions"][index], TIERS[index])


def format_special_achievement(key: str) -> str:
    """
    Formats a special achievement.
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
    format_string: str, tier_requirements: AchievementTierRequirements
) -> AchievementTierDescriptions:
    """
    Gets tiered achievement descriptions based on requirements for each
    tier and a format string to put the number for each tier into.
    """
    return AchievementTierDescriptions(
        *(format_string.format(value) for value in tier_requirements))


def get_achievement_count() -> int:
    """
    Returns the number of achievements earned by the player.
    """
    # Boolean sum - treat a completed special achievement as 1
    # and an incomplete one as 0.
    achievement_count = sum(get_special_achievements().values())

    for key, value in TIERED_ACHIEVEMENTS.items():
        if key == "achievements":
            continue
        result = value["function"]()
        for requirement in value["requirements"]:
            if result < requirement:
                break
            achievement_count += 1
    for requirement in TIERED_ACHIEVEMENTS["achievements"]["requirements"]:
        if achievement_count < requirement:
            break
        achievement_count += 1

    return achievement_count


# Milestones which each count as an achievement.
TIERED_ACHIEVEMENTS = {
    "games_played": create_tiered_achievement(
        "Countdown Commitment", stats.get_games_played,
        (requirements := AchievementTierRequirements(10, 50, 250, 2500)),
        get_tiered_achievement_descriptions("Play {} games", requirements)),

    "wins": create_tiered_achievement(
        "Getting good at maths!", stats.get_win_count,
        (requirements := AchievementTierRequirements(5, 25, 125, 1000)),
        get_tiered_achievement_descriptions("Win {} games", requirements)),

    "time_played": create_tiered_achievement(
        "Time flies when you're having fun", stats.get_seconds_played,
        # In seconds played.
        AchievementTierRequirements(1200, 7200, 36000, 180000),
        AchievementTierDescriptions(
            *(
                "Play {}".format(duration) for duration in (
                    "20 minutes", "2 hours", "10 hours", "50 hours")))),

    "level": create_tiered_achievement(
        "Expertise Development", stats.get_total_xp,
        # By XP - nicer and easier to handle.
        AchievementTierRequirements(
            *(level.get_total_xp_for_level(lvl) for lvl in (5, 12, 25, 75))),
        AchievementTierDescriptions(
            *("Reach level {}".format(lvl) for lvl in (5, 12, 25, 75)))),

    "best_streak": create_tiered_achievement(
        "Winner Winner Chicken Dinner", stats.get_best_win_streak,
        (requirements := AchievementTierRequirements(2, 5, 20, 78)),
        get_tiered_achievement_descriptions(
            "Reach a win streak of {}", requirements)),

    "achievements": create_tiered_achievement(
        "Achievement for achievements", get_achievement_count,
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
        "OOPS!", "Submit an incorrect solution.", "bronze"),

    "small_numbers": create_special_achievement(
        "Small numbers reign!",
        "Find a solution using exactly 5 small numbers and 0 big numbers.",
        "gold"),

    "big_numbers": create_special_achievement(
        "Brutal big numbers!",
        "Find a solution using exactly 5 big numbers and 0 small numbers.",
        "gold"),

    "all_numbers": create_special_achievement(
        "Full House!",
        "Find a solution using all the numbers provided.", "silver"),

    "all_operators": create_special_achievement(
        "Together they are strong!",
        "Use all operators in a solution.", "silver"),

    "one_operator": create_special_achievement(
        "One Operator!", "Find a solution using only one operator.", "gold")
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
        self.pages_frame = AchievementsPagesFrame(self)
        self.back_button = tk.Button(
            self, font=ink_free(25), text="Back", width=10, border=5,
            bg=ORANGE, activebackground=RED, command=self.back)

        self.title_label.pack(padx=10, pady=5)
        self.pages_frame.pack(padx=10, pady=5)
        self.back_button.pack(padx=10, pady=5)

    def back(self) -> None:
        """
        Returns back to the main menu.
        """
        self.destroy()
        menu.MainMenu(self.root).pack()


class TieredAchievementLabelFrame(tk.LabelFrame):
    """
    Holds a tiered achievement by its key.
    """

    def __init__(self, master: tk.Frame, key: str) -> None:
        achievement = TIERED_ACHIEVEMENTS[key]
        super().__init__(
            master, font=ink_free(25, italic=True),
            text=achievement["name"], labelanchor="n")

        self.result = achievement["function"]()
        # Final value of requirement is indeed the
        # requirement for the next tier.
        for i, requirement in enumerate(achievement["requirements"]):
            if self.result < requirement:
                if i > 0: # At least Bronze attained.
                    self.config(fg=(BRONZE, SILVER, GOLD)[i - 1])
                self.description_label = tk.Label(
                    self, font=ink_free(15),
                    text=achievement["descriptions"][i])
                break
        else:
            # Fully complete - max tier (Platinum) reached.
            self.config(fg=PLATINUM)
            self.description_label = tk.Label(
                self, font=ink_free(15, True), fg=GREEN,
                text=f"{achievement['descriptions'][-1]} [Complete]")

        self.requirement = requirement
        self.progress_bar = widgets.ProgressBar(
            self, min(1, round(self.result / self.requirement, 10)), 200, 8)
        self.progress_label = tk.Label(
            self, font=ink_free(15),
            text=f"{self.result} / {self.requirement}")

        self.description_label.pack(padx=10)
        self.progress_bar.pack(padx=10, pady=3)
        self.progress_label.pack(padx=10)


class TimePlayedAchievementFrame(TieredAchievementLabelFrame):
    """
    Holds the time played achievement specifically as its display
    changes units for different tiers of the achievement.
    """

    def __init__(self, master: tk.Frame) -> None:
        super().__init__(master, "time_played")
        self.progress_label.config(
            text="{} / {}".format(
                *map(seconds_to_hhmmss, (self.result, self.requirement))))


class LevelAchievementFrame(TieredAchievementLabelFrame):
    """
    Holds the level achievement specifically to display
    the level progress instead of the XP progress to the player.
    """

    def __init__(self, master: tk.Frame) -> None:
        super().__init__(master, "level")
        self.progress_label.config(
            text="{} / {}".format(
                level.get_level(), level.get_level(self.requirement)))


class SpecialAchievementLabelFrame(tk.LabelFrame):
    """
    Holds a special achievement, simply displaying its
    name, description, tier and completion status.
    """

    def __init__(self, master: tk.Frame, key: str) -> None:
        achievement = SPECIAL_ACHIEVEMENTS[key]
        super().__init__(
            master, font=ink_free(25, italic=True),
            text=achievement["name"], labelanchor="n")

        self.description_label = tk.Label(
            self, font=ink_free(15),
            text=f"{achievement['description']} ({achievement['tier']})")

        if get_special_achievement(key):
            self.config(
                fg=(BRONZE, SILVER, GOLD, PLATINUM)
                    [TIERS.index(achievement["tier"])])
            self.status_label = tk.Label(
                self, font=ink_free(15, True), text="Complete!", fg=GREEN)
        else:
            self.status_label = tk.Label(
                self, font=ink_free(15), text="Incomplete", fg=RED)

        self.description_label.pack(padx=10, pady=5)
        self.status_label.pack(padx=10, pady=5)


class AchievementsPagesFrame(widgets.PagesFrame):
    """
    Allows the player to view the different pages of
    achievements - they cannot all fit on one page.
    """

    def __init__(self, master: AchievementsWindow) -> None:
        super().__init__(master, 1, PAGE_COUNT, width=1200, height=400)
        page_1 = tk.Frame(self)
        page_1_achievements = (
            TieredAchievementLabelFrame(page_1, key)
            if key != "time_played" else TimePlayedAchievementFrame(page_1)
            for key in tuple(TIERED_ACHIEVEMENTS)[:3])
        next(page_1_achievements).grid(row=0, column=0, padx=10, pady=10)
        next(page_1_achievements).grid(row=0, column=1, padx=10, pady=10)
        next(page_1_achievements).grid(
            row=1, column=0, columnspan=2, padx=10, pady=10)
        self.add(page_1)

        page_2 = tk.Frame(self)
        page_2_achievements = (
            TieredAchievementLabelFrame(page_2, key)
            if key != "level" else LevelAchievementFrame(page_2)
            for key in tuple(TIERED_ACHIEVEMENTS)[3:])
        next(page_2_achievements).grid(row=0, column=0, padx=10, pady=10)
        next(page_2_achievements).grid(row=0, column=1, padx=10, pady=10)
        next(page_2_achievements).grid(
            row=1, column=0, columnspan=2, padx=10, pady=10)
        self.add(page_2)

        # Special achievements: pages 3 and 4
        for achievements in (
            tuple(SPECIAL_ACHIEVEMENTS)[:4], tuple(SPECIAL_ACHIEVEMENTS)[4:]
        ):
            page = tk.Frame(self)
            page_achievements = (
                SpecialAchievementLabelFrame(page, key)
                for key in achievements)
            for i, achievement in enumerate(page_achievements):
                # 2x2 grid (0,0), (0,1), (1,0), (1,1) (x=row, y=column)
                achievement.grid(row=i // 2, column=i % 2, padx=10, pady=5)
            self.add(page)

        self.show()
