import os
import gzip
import shutil
from contextlib import suppress
from typing import Callable

import ujson as json


FOLDER = "./data"
STREAK_FILE = f"{FOLDER}/streak.dat"
XP_FILE = f"{FOLDER}/xp.dat"
RECENT_NUMBERS_FILE = f"{FOLDER}/recent_numbers.json"

GAME_DATA_FOLDER = f"{FOLDER}/game_data"

MAX_RECENT_NUMBERS_COUNT = 25
# Split game data into multiple files, so only a fairly small chunk
# of data has to be rewritten to add new data.
MAX_GAME_DATA_PER_FILE = 100


def check_folder_exists(folder: str = FOLDER) -> Callable:
    """
    Ensures a folder exists, or else, creates it.
    """
    def decorator(function: Callable) -> Callable:
        def wrap(*args, **kwargs):
            with suppress(FileExistsError):
                os.mkdir(folder)
            return function(*args, **kwargs)
        return wrap
    return decorator


@check_folder_exists()
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


@check_folder_exists()
def increment_win_streak() -> None:
    """
    Increases win streak by 1
    """
    new_streak = get_win_streak() + 1
    with open(STREAK_FILE, "wb") as f:
        f.write(str(new_streak).encode())


@check_folder_exists()
def reset_win_streak() -> None:
    """
    Resets win streak to 0
    """
    with open(STREAK_FILE, "wb") as f:
        f.write(b"0")


@check_folder_exists()
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


@check_folder_exists()
def add_total_xp(xp: int) -> None:
    """
    Adds to the total XP earned by the player.
    """
    new_total_xp = get_total_xp() + xp
    with open(XP_FILE, "wb") as f:
        f.write(str(new_total_xp).encode())


@check_folder_exists()
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


@check_folder_exists()
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


@check_folder_exists()
@check_folder_exists(GAME_DATA_FOLDER)
def get_game_data() -> list[dict]:
    """
    Gets data for all game rounds played in the past.
    """
    try:
        files = map(
            lambda file: f"{GAME_DATA_FOLDER}/{file}",
            sorted(os.listdir(GAME_DATA_FOLDER), key=int))
        game_data = []
        for file in files:
            with gzip.open(file, "rt", encoding="utf8") as f:
                data = json.load(f)
            game_data.extend(data)
        return game_data
    except Exception:
        # Corruption
        shutil.rmtree(GAME_DATA_FOLDER)
        return []


@check_folder_exists()
@check_folder_exists(GAME_DATA_FOLDER)
def add_game_data(new_data: dict) -> None:
    """
    Adds game data.
    """
    # Newest file has largest number (-1 if empty).
    newest = max(map(int, os.listdir(GAME_DATA_FOLDER) or [-1]))
    try:
        if newest != -1:
            file = f"{GAME_DATA_FOLDER}/{newest}"
            with gzip.open(file, "rt", encoding="utf8") as f:
                data = json.load(f)
            if len(data) < MAX_GAME_DATA_PER_FILE:
                data.append(new_data)
                with gzip.open(file, "wt", encoding="utf8") as f:
                    json.dump(data, f, separators=(",", ":"))
                return

        new_file = f"{GAME_DATA_FOLDER}/{newest + 1}"
        with gzip.open(new_file, "wt", encoding="utf8") as f:
            json.dump([new_data], f, separators=(",", ":"))
    except Exception:
        # Corruption
        shutil.rmtree(GAME_DATA_FOLDER)