import os
import json
from contextlib import suppress
from typing import Callable


FOLDER = "./data"
STREAK_FILE = f"{FOLDER}/streak.dat"
XP_FILE = f"{FOLDER}/xp.dat"
RECENT_NUMBERS_FILE = f"{FOLDER}/recent_numbers.json"

MAX_RECENT_NUMBERS_COUNT = 25


def check_folder_exists(function: Callable) -> Callable:
    """
    Ensures data folder exists, or else,
    create the data folder.
    """
    def wrap(*args, **kwargs):
        while True:
            try:
                return function(*args, **kwargs)
            except FileNotFoundError:
                with suppress(FileExistsError):
                    os.mkdir(FOLDER)
    return wrap


@check_folder_exists
def get_win_streak() -> int:
    """
    Gets number of rounds the player has won consecutively.
    """
    try:
        with open(STREAK_FILE, "rb") as f:
            streak = int(f.read())
            if streak < 0:
                raise ValueError
            return streak
    except (FileNotFoundError, ValueError):
        # File does not exist or is corrupt.
        with open(STREAK_FILE, "wb") as f:
            f.write(b"0")
        return 0


@check_folder_exists
def increment_win_streak() -> None:
    """
    Increases win streak by 1
    """
    new_streak = get_win_streak() + 1
    with open(STREAK_FILE, "wb") as f:
        f.write(str(new_streak).encode())


@check_folder_exists
def reset_win_streak() -> None:
    """
    Resets win streak to 0
    """
    with open(STREAK_FILE, "wb") as f:
        f.write(b"0")


@check_folder_exists
def get_total_xp() -> int:
    """
    Gets the total XP earned by the player.
    """
    try:
        with open(XP_FILE, "rb") as f:
            xp = int(f.read())
            if xp < 0:
                raise ValueError
            return xp
    except (FileNotFoundError, ValueError):
        # File does not exist or is corrupt.
        with open(XP_FILE, "wb") as f:
            f.write(b"0")
        return 0


@check_folder_exists
def add_total_xp(xp: int) -> None:
    """
    Adds to the total XP earned by the player.
    """
    new_total_xp = get_total_xp() + xp
    with open(XP_FILE, "wb") as f:
        f.write(str(new_total_xp).encode())


@check_folder_exists
def get_recent_numbers() -> list[int]:
    """
    Gets the most recently randomly generated target numbers.
    """
    try:
        with open(RECENT_NUMBERS_FILE, "r", encoding="utf8") as f:
            recent = json.load(f)
            # Checks if recent numbers are valid.
            if len(recent) > MAX_RECENT_NUMBERS_COUNT or not all(
                isinstance(number, int) and 201 <= number <= 999
                for number in recent
            ):
                raise ValueError
            return recent
    except (FileNotFoundError, ValueError):
        # File does not exist or is corrupt.
        with open(RECENT_NUMBERS_FILE, "w", encoding="utf8") as f:
            json.dump([], f)
        return []


@check_folder_exists
def add_recent_number(number: int) -> None:
    """
    Adds a randomly generated target number to the recent numbers.
    """
    recent = get_recent_numbers()
    recent.insert(0, number)
    if len(recent) > MAX_RECENT_NUMBERS_COUNT:
        recent.pop()
    with open(RECENT_NUMBERS_FILE, "w", encoding="utf8") as f:
        json.dump(recent, f)