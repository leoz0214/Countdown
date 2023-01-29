"""
Utilities for file handling in the application.
"""
import os
import shutil
from contextlib import suppress
from typing import Callable


FOLDER = f"{os.getenv('LOCALAPPDATA')}/CountdownGame/data"
TEMPORARY_FOLDER = f"{FOLDER}/temp"


def check_folder_exists(folder: str = FOLDER) -> Callable:
    """
    Decorator which ensures a folder exists, or else, creates it.
    Also creates any non-existent required parent folders.
    """
    def decorator(function: Callable) -> Callable:
        def wrap(*args, **kwargs) -> Callable:
            for i, char in enumerate(folder + "/"):
                if char == "/" and not folder[:i].endswith(":"):
                    with suppress(FileExistsError):
                        os.mkdir(folder[:i])
            return function(*args, **kwargs)
        return wrap
    return decorator


@check_folder_exists(TEMPORARY_FOLDER)
def create_temp_folder() -> None:
    """
    Creates the temporary folder, if it does not already exist.
    """
    return


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
