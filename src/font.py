def ink_free(size: int, bold: bool = False, italic: bool = False) -> tuple:
    """
    Utility function for 'Ink Free' font.
    """
    font = ("Ink Free", size)
    if bold:
        font += ("bold",)
    if italic:
        font += ("italic",)
    return font