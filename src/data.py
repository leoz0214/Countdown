import os
import json


FOLDER = "./data"
STREAK_FILE = f"{FOLDER}/streak.dat"
XP_FILE = f"{FOLDER}/xp.dat"
RECENT_NUMBERS_FILE = f"{FOLDER}/recent_numbers.json"

MAX_RECENT_NUMBERS_COUNT = 25


def get_win_streak() -> int:
    """
    Gets number of rounds the player has won consecutively.
    """
    if not os.path.isfile(STREAK_FILE):
        with open(STREAK_FILE, "wb") as f:
            f.write(b"0")
        return 0
    
    try:
        with open(STREAK_FILE, "rb") as f:
            return int(f.read())
    except ValueError:
        # File is corrupt.
        with open(STREAK_FILE, "wb") as f:
            f.write(b"0")
        return 0


def increment_win_streak() -> None:
    """
    Increases win streak by 1
    """
    new_streak = get_win_streak() + 1
    with open(STREAK_FILE, "wb") as f:
        f.write(str(new_streak).encode())


def reset_win_streak() -> None:
    """
    Resets win streak to 0
    """
    with open(STREAK_FILE, "wb") as f:
        f.write(b"0")


def get_total_xp() -> int:
    """
    Gets the total XP earned by the player.
    """
    if not os.path.isfile(XP_FILE):
        with open(XP_FILE, "wb") as f:
            f.write(b"0")
        return 0
    
    try:
        with open(XP_FILE, "rb") as f:
            return int(f.read())
    except ValueError:
        # File is corrupt.
        with open(XP_FILE, "wb") as f:
            f.write(b"0")
        return 0


def add_total_xp(xp: int) -> None:
    """
    Adds to the total XP earned by the player.
    """
    new_total_xp = get_total_xp() + xp
    with open(XP_FILE, "wb") as f:
        f.write(str(new_total_xp).encode())


def get_recent_numbers() -> list[int]:
    """
    Gets the most recently randomly generated target numbers.
    """
    if not os.path.isfile(RECENT_NUMBERS_FILE):
        with open(RECENT_NUMBERS_FILE, "w", encoding="utf8") as f:
            json.dump([], f)
        return []
    
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
    except ValueError:
        # File is corrupt
        with open(RECENT_NUMBERS_FILE, "w", encoding="utf8") as f:
            json.dump([], f)
        return []


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