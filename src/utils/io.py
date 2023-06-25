"""
Utilities for file handling in the application.
"""
import os
import pathlib
import shutil
import threading
from contextlib import suppress
from typing import Callable


FOLDER = pathlib.Path(os.getenv("LOCALAPPDATA")) / "CountdownGame" / "data"
TEMPORARY_FOLDER = FOLDER / "temp"
LOCK_FILE = FOLDER / "lock"


def check_folder_exists(folder: str = FOLDER) -> Callable:
    """
    Decorator which ensures a folder exists, or else, creates it.
    Also creates any non-existent required parent folders.
    """
    def decorator(function: Callable) -> Callable:
        def wrap(*args, **kwargs) -> Callable:
            for i, char in enumerate(f"{folder}/"):
                if char == "/" and not str(folder)[:i].endswith(":"):
                    with suppress(FileExistsError):
                        os.mkdir(str(folder)[:i])
            return function(*args, **kwargs)
        return wrap
    return decorator


def create_temp_folder() -> None:
    """
    Creates the temporary folder, if it does not already exist.
    """
    TEMPORARY_FOLDER.mkdir(parents=True, exist_ok=True)


def remove_temp_folder() -> None:
    """
    Deletes the temporary folder, if it exists.
    """
    with suppress(FileNotFoundError):
        shutil.rmtree(TEMPORARY_FOLDER)


def reset_data() -> None:
    """
    Resets player data simply by deleting the data folder.
    """
    with suppress(FileNotFoundError):
        shutil.rmtree(FOLDER)


def get_lockfile_value() -> int:
    """
    Retrieves the current number stored in the lockfile,
    -1 if it does not exist.
    """
    if not LOCK_FILE.exists():
        return -1
    return int(LOCK_FILE.read_text())


def increment_lockfile_value() -> int:
    """Increases the number stored in the lockfile by 1."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    value = get_lockfile_value() + 1
    LOCK_FILE.write_text(str(value))
