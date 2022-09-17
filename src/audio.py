from pygame import mixer


mixer.init()


def get_sfx(filename: str) -> mixer.Sound:
    """
    Fetches the SFX with a particular filename,
    returning a pygame Sound object.
    Path not required, just the name of the file.
    """
    path = f"./audio/sfx/{filename}"
    return mixer.Sound(path)


def get_music(filename: str) -> mixer.Sound:
    """
    Fetches the music with a particular filename,
    returning a pygame Sound object.
    Path not required, just the name of the file.
    """
    path = f"./audio/music/{filename}"
    return mixer.Sound(path)