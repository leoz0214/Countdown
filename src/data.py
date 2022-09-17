import os


FOLDER = "./data"
STREAK_FILE = f"{FOLDER}/streak.dat"


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