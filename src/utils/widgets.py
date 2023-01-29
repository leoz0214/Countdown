"""
Convenient utility widgets which have high reusability.
"""
import tkinter as tk

from .colours import *
from .utils import ink_free, bool_to_state


class PagesFrame(tk.Frame):
    """
    Supports pages which can be cycled through.
    """

    def __init__(
        self, master: tk.Frame, starting_page_number: int,
        page_count: int, width: int, height: int
    ) -> None:
        super().__init__(master, width=width, height=height)
        self.pack_propagate(False)
        self.pages = []

        self.first_page = 1
        self.last_page = page_count
        self.current_page = starting_page_number
        self.total_pages = page_count

        self.navigation_frame = PageNavigationFrame(self)
        self.navigation_frame.pack(padx=10, pady=10)

    def add(self, page: tk.Frame) -> None:
        """
        Adds a page to the frame.
        """
        self.pages.append(page)

    def show(self) -> None:
        """
        Displays the current page.
        """
        self.pages[self.current_page - 1].pack(padx=10, pady=10)


class PageNavigationFrame(tk.Frame):
    """
    Allows the page number to be changed.
    """

    def __init__(self, master: PagesFrame) -> None:
        super().__init__(master)
        self.master = master
        self.back_button = tk.Button(
            self, font=ink_free(25), text="<", width=3, border=5,
            bg=ORANGE, activebackground=GREEN, command=self.back,
            state=bool_to_state(
                self.master.current_page != self.master.first_page))
        self.current_page_label = tk.Label(
            self, font=ink_free(25), width=8,
            text=f"{self.master.current_page} / {self.master.total_pages}")
        self.forward_button = tk.Button(
            self, font=ink_free(25), text=">", width=3, border=5,
            bg=ORANGE, activebackground=GREEN, command=self.forward,
            state=bool_to_state(
                self.master.current_page != self.master.last_page))

        self.back_button.pack(side="left")
        self.current_page_label.pack(side="left")
        self.forward_button.pack()

    def back(self) -> None:
        """
        Move back a page.
        """
        self.master.pages[self.master.current_page - 1].pack_forget()
        self.master.current_page -= 1
        self.current_page_label.config(
            text=f"{self.master.current_page} / {self.master.total_pages}")
        if self.master.current_page == self.master.first_page:
            self.back_button.config(state="disabled")
        # Can definitely go forward (not currently on the last page).
        self.forward_button.config(state="normal")
        self.master.pages[self.master.current_page - 1].pack(padx=10, pady=10)

    def forward(self) -> None:
        """
        Move forward a page.
        """
        self.master.pages[self.master.current_page - 1].pack_forget()
        self.master.current_page += 1
        self.current_page_label.config(
            text=f"{self.master.current_page} / {self.master.total_pages}")
        if self.master.current_page == self.master.last_page:
            self.forward_button.config(state="disabled")
        # Can definitely go back (not currently on the first page).
        self.back_button.config(state="normal")
        self.master.pages[self.master.current_page - 1].pack(padx=10, pady=10)


class ProgressBar(tk.Canvas):
    """
    Visually shows progress towards something,
    such as the next level or an achievement.
    """

    def __init__(
        self, master: tk.Widget, progress: float, width: int, height: int
    ) -> None:
        super().__init__(master, width=width, height=height)
        self.create_rectangle(0, 0, int(width * progress), height, fill=GREEN)
        self.create_rectangle(
            int(width * progress), 0, width, height, fill=GREY)
