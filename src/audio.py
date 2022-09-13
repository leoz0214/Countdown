from pygame import mixer


mixer.init()


def get_sfx(file_name: str) -> mixer.Sound:
    """
    Fetches the SFX with a particular filename,
    returning a pygame Sound object.
    Path not required, just the name of the file.
    """
    path = f"./audio/sfx/{file_name}"
    return mixer.Sound(path)


def get_music(file_name: str) -> mixer.Sound:
    """
    Fetches the music with a particular filename,
    returning a pygame Sound object.
    Path not required, just the name of the file.
    """
    path = f"./audio/music/{file_name}"
    return mixer.Sound(path)