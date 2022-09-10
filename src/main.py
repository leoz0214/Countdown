import tkinter as tk

import menu
from colours import *


def main() -> None:
    """
    Main function of app.
    """
    root = tk.Tk()
    root.tk_setPalette(background=DEFAULT_BACKGROUND, foreground=BLACK)
    main_menu = menu.MainMenu(root)
    main_menu.pack()
    root.mainloop()


if __name__ == "__main__":
    main()