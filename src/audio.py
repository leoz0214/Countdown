from pygame import mixer

mixer.init()


def get_sfx(filename: str) -> mixer.Sound:
    """
    Fetches the SFX with a particular filename,
    returning a pygame Sound object.
    Path not required, just the name of the file.
    """
    return mixer.Sound(f"./audio/sfx/{filename}")


def get_music(filename: str) -> mixer.Sound:
    """
    Fetches the music with a particular filename,
    returning a pygame Sound object.
    Path not required, just the name of the file.
    """
    return mixer.Sound(f"./audio/music/{filename}")