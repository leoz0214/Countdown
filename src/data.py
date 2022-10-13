import os
import gzip
import shutil
import time
from contextlib import suppress
from typing import Callable

try:
    # Faster json module.
    import ujson as json
except ImportError:
    print("Warning: ujson not found, using built-in json instead.")
    import json


OPERATORS = "+-x÷"

FOLDER = "./data"
STREAK_FILE = f"{FOLDER}/streak.dat"
RECENT_NUMBERS_FILE = f"{FOLDER}/recent_numbers.json"

STATS_FOLDER = f"{FOLDER}/stats"
XP_FILE = f"{STATS_FOLDER}/xp.dat"
GAMES_PLAYED_FILE = f"{STATS_FOLDER}/played.dat"
GAMES_WON_FILE = f"{STATS_FOLDER}/won.dat"
BEST_WIN_STREAK_FILE = f"{STATS_FOLDER}/best_streak.dat"
SMALL_NUMBERS_FILE = f"{STATS_FOLDER}/small.dat"
BIG_NUMBERS_FILE = f"{STATS_FOLDER}/big.dat"
SECONDS_PLAYED_FILE = f"{STATS_FOLDER}/time.dat"
OPERATORS_USED_FILE = f"{STATS_FOLDER}/operators.json"

GAME_DATA_FOLDER = f"{FOLDER}/game_data"

MAX_RECENT_NUMBERS_COUNT = 25
# Split game data into multiple files, so only a fairly small chunk
# of data has to be rewritten to add new data.
MAX_GAME_DATA_PER_FILE = 100
# Number of recent games which can be stored without time limit.
# Beyond that, game data older than 30 days is deleted.
MAX_ALLOWED_GAME_DATA = 1000

SECONDS_IN_30_DAYS = 2_592_000


def check_folder_exists(folder: str = FOLDER) -> Callable:
    """
    Ensures a folder exists, or else, creates it.
    """
    def decorator(function: Callable) -> Callable:
        def wrap(*args, **kwargs) -> Callable:
            with suppress(FileExistsError):
                os.mkdir(folder)
            return function(*args, **kwargs)
        return wrap
    return decorator


def get_incremental_data_functions(
    file: str, required_folders: tuple[str] | None = None) -> tuple[Callable]:
    """
    Creates simple incremental data functions to be used for a variety
    of data that needs to be stored in this program.
    """
    def get() -> int:
        try:
            with open(file, "rb") as f:
                value = int(f.read())
            if value < 0:
                raise ValueError
            return value
        except (FileNotFoundError, ValueError):
            # File does not exist or is corrupt.
            with open(file, "wb") as f:
                f.write(b"0")
            return 0

    def increment() -> None:
        new = get() + 1
        with open(file, "wb") as f:
            f.write(str(new).encode())

    if required_folders:
        # Checks in reverse - least nested folders checked for first.
        for folder in reversed(required_folders):
            get = check_folder_exists(folder)(get)
            increment = check_folder_exists(folder)(increment)
    get = check_folder_exists()(get)
    increment = check_folder_exists()(increment)
    return get, increment


def get_additive_data_functions(
    file: str, required_folders: tuple[str] | None = None, 
    data_type: type = int) -> tuple[Callable]:
    """
    Creates simple additive data functions (for adding to a number).
    """
    def get() -> int | float:
        try:
            with open(file, "rb") as f:
                value = data_type(f.read())
            if value < 0:
                raise ValueError
            return value
        except (FileNotFoundError, ValueError):
            # File does not exist or is corrupt.
            with open(file, "wb") as f:
                f.write(b"0")
            return 0
    
    def add(value: int | float) -> None:
        new = get() + value
        with open(file, "wb") as f:
            f.write(str(new).encode())

    if required_folders:
        for folder in reversed(required_folders):
            get = check_folder_exists(folder)(get)
            add = check_folder_exists(folder)(add)
    get = check_folder_exists()(get)
    add = check_folder_exists()(add)
    return get, add


get_win_streak, increment_win_streak = (
    get_incremental_data_functions(STREAK_FILE))

get_games_played, increment_games_played = (
    get_incremental_data_functions(GAMES_PLAYED_FILE, (STATS_FOLDER,)))

get_win_count, increment_win_count = (
    get_incremental_data_functions(GAMES_WON_FILE, (STATS_FOLDER,)))

get_best_win_streak, increment_best_win_streak = (
    get_incremental_data_functions(BEST_WIN_STREAK_FILE, (STATS_FOLDER,)))

get_total_xp, add_total_xp = (
    get_additive_data_functions(XP_FILE, (STATS_FOLDER,)))

get_small_numbers_used, add_small_numbers_used = (
    get_additive_data_functions(SMALL_NUMBERS_FILE, (STATS_FOLDER,)))

get_big_numbers_used, add_big_numbers_used = (
    get_additive_data_functions(BIG_NUMBERS_FILE, (STATS_FOLDER,)))

get_seconds_played, add_seconds_played = (
    get_additive_data_functions(SECONDS_PLAYED_FILE, (STATS_FOLDER,), float))


@check_folder_exists()
def reset_win_streak() -> None:
    """
    Resets win streak to 0
    """
    with open(STREAK_FILE, "wb") as f:
        f.write(b"0")


@check_folder_exists()
@check_folder_exists(STATS_FOLDER)
def get_operators_used() -> dict[str, int]:
    """
    Gets the number of times each operator has been used:
    addition, subtraction, multiplication and division.
    """
    try:
        with open(OPERATORS_USED_FILE, "r", encoding="utf8") as f:
            operators_used = json.load(f)
        # Checks data is valid.
        if (
            not isinstance(operators_used, dict) or len(operators_used) != 4
            or "".join(operators_used.keys()) != OPERATORS or
            any(
                count < 0 or not isinstance(count, int)
                for count in operators_used.values())
        ):
            raise ValueError
        return operators_used
    except (FileNotFoundError, ValueError):
        new = {operator: 0 for operator in OPERATORS}
        with open(OPERATORS_USED_FILE, "w", encoding="utf8") as f:
            json.dump(new, f)
        return new


@check_folder_exists()
@check_folder_exists(STATS_FOLDER)
def add_operators_used(operators_used: dict[str, int]) -> None:
    """
    Adds operators used to the total.
    """
    new = get_operators_used()
    for operator, used in operators_used.items():
        new[operator] += used
    with open(OPERATORS_USED_FILE, "w", encoding="utf8") as f:
        json.dump(new, f)


@check_folder_exists()
def get_recent_numbers() -> list[int]:
    """
    Gets the most recently randomly generated target numbers.
    """
    try:
        with open(RECENT_NUMBERS_FILE, "r", encoding="utf8") as f:
            recent = json.load(f)
        # Checks if recent numbers are valid.
        if (
            not isinstance(recent, list)
            or len(recent) > MAX_RECENT_NUMBERS_COUNT
            or not all(
                isinstance(number, int) and 201 <= number <= 999
                for number in recent)
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


def remove_expired_games(
    files: list[str], final_file_check_limit: int) -> list[str]:
    """
    Removes expired games (ones that finished more than 30 days ago).
    Games older than 30 days are allowed if there are not too many.
    Returns new files (may be the same if no deletion required).
    """
    index = len(files) // 2
    current_timestamp = time.time()
    found_expired = False
    final = files[-1]
    while True:
        with gzip.open(files[index], "rt", encoding="utf8") as f:
            data = json.load(f)
        for i, game in enumerate(data.copy()):
            if files[index] == final and i >= final_file_check_limit:
                break
            if current_timestamp - game["stop_time"] > SECONDS_IN_30_DAYS:
                if not found_expired:
                    found_expired = True
                data.remove(game)

        if found_expired:
            for file in files[:index]:
                os.remove(file)
            if data:
                # Current file only partially expired.
                with gzip.open(files[index], "wt", encoding="utf8") as f:
                    json.dump(data, f)
                # Can now just continue - all expired files removed.
                files = files[index:]
                break
            else:
                os.remove(files[index])
                # Restart the process.
                files = files[index + 1:]
                index = len(files) // 2
                found_expired = False
                continue
            
        if not index or not files:
            break
        index //= 2
    return files


@check_folder_exists()
@check_folder_exists(GAME_DATA_FOLDER)
def get_game_data() -> list[dict]:
    """
    Gets data for all game rounds played in the past.
    """
    try:
        files = list(map(
            lambda file: f"{GAME_DATA_FOLDER}/{file}",
            sorted(os.listdir(GAME_DATA_FOLDER), key=int)))
        if not files:
            return []
        
        # If maximum number of game data with n files is greater
        # than max, check to remove expired data.
        # n files: 1 + 100 * (n - 2) + 1
        if len(files) * MAX_GAME_DATA_PER_FILE > MAX_ALLOWED_GAME_DATA:
            with gzip.open(files[-1], "rt", encoding="utf8") as f:
                last_file_game_data_count = len(json.load(f))
            
            # Number of ending files guaranteed to be allowed to stay.
            allowed_ending_file_count = (
                (MAX_ALLOWED_GAME_DATA - last_file_game_data_count)
                // MAX_GAME_DATA_PER_FILE) + 1
            
            # How far the newest uncertain file may require removal.
            before_allowed_possibly_expired_data_count = (
                (MAX_ALLOWED_GAME_DATA -
                (
                    (MAX_ALLOWED_GAME_DATA // MAX_GAME_DATA_PER_FILE - 1)
                    * MAX_GAME_DATA_PER_FILE)
                ) - (MAX_GAME_DATA_PER_FILE - last_file_game_data_count))
            
            allowed_files = files[-allowed_ending_file_count:]
        
            files = remove_expired_games(
                files[:-allowed_ending_file_count],
                before_allowed_possibly_expired_data_count) + allowed_files

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