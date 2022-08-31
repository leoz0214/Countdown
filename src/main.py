import tkinter as tk

import countdown


def main() -> None:
    """
    Main function of app.
    """
    root = tk.Tk()
    root.tk_setPalette(background="white", foreground="black")
    countdown.MainMenu(root).pack()
    root.mainloop()


if __name__ == "__main__":
    main()