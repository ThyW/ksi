#! /usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox
from impl import Mtp, Meme
import os
from time import sleep

from typing import List, Optional

BG = "#282828"
FG = "#ebdbb2"
RED = "#cc241d"
GRAY = "#504945"
YELLOW = "#fabd2f"
BLUE = "#458588"


class Gui:
    def __init__(self) -> None:
        # main window
        self.window = tk.Tk()
        self.window.title("MTP Client")
        self.window.configure(bg=BG)
        self.window.grid_rowconfigure(2, minsize=20)
        self.window.grid_rowconfigure(4, minsize=20)
        self.constructed_meme: Optional[Meme] = None

        # tkinter variables
        self.nsfw_var = tk.IntVar(value=0)

        # entries and checkboxes and labels
        self.username_l = tk.Label(self.window,
                                   text="username: ",
                                   bg=BG,
                                   fg=YELLOW,
                                   highlightbackground=BG)
        self.username_e = tk.Entry(self.window,
                                   bg=BG,
                                   fg=FG,
                                   highlightbackground=BG)
        self.password_l = tk.Label(self.window,
                                   text="password: ",
                                   bg=BG,
                                   fg=YELLOW,
                                   highlightbackground=BG)
        self.password_e = tk.Entry(self.window,
                                   bg=BG,
                                   fg=FG,
                                   highlightbackground=BG)
        self.description_l = tk.Label(self.window,
                                      text="description: ",
                                      bg=BG,
                                      fg=YELLOW,
                                      highlightbackground=BG)
        self.description_e = tk.Text(self.window,
                                     width=23,
                                     height=3,
                                     font="Iosevka",
                                     bg=BG,
                                     fg=FG,
                                     highlightbackground=BG)
        self.is_nsfw = tk.Checkbutton(self.window,
                                      text="NSFW",
                                      onvalue=1,
                                      offvalue=0,
                                      variable=self.nsfw_var,
                                      bg=BG,
                                      fg=YELLOW,
                                      highlightbackground=BG,
                                      activebackground=BLUE,
                                      activeforeground=RED)

        # buttons
        self.construct_meme_b = tk.Button(self.window,
                                          text="CONSTRUCT MEME",
                                          command=self.construct_meme,
                                          bg=BG,
                                          foreground=YELLOW,
                                          highlightbackground=BG,
                                          activebackground=BLUE,
                                          activeforeground=RED)
        self.run_b = tk.Button(self.window,
                               text="RUN",
                               command=self.run_func,
                               bg=BG,
                               foreground=YELLOW,
                               highlightbackground=BG,
                               activebackground=BLUE,
                               activeforeground=RED)
        self.image = tk.Label(self.window,
                              text="No meme chosen!",
                              bg=BG,
                              foreground=FG,
                              highlightbackground=BG,
                              activebackground=BLUE,
                              activeforeground=RED)
        # self.img_l = tk.Label(self.window,
        #                       text="choose a meme:",
        #                       bg=BG,
        #                       foreground=FG,
        #                       highlightbackground=BG)
        self.browse_img_b = tk.Button(self.window,
                                      text="BROWSE",
                                      bg=BG,
                                      foreground=YELLOW,
                                      highlightbackground=BG,
                                      command=self.ask_filename,
                                      activebackground=BLUE,
                                      activeforeground=RED)

        self.username_l\
            .grid(row=0, column=0, sticky=tk.NE, padx=30, pady=10)
        self.username_e\
            .grid(row=0, column=1, sticky=tk.NW, pady=10)
        self.password_l\
            .grid(row=0, column=2, sticky=tk.NW, pady=10, padx=30)
        self.password_e\
            .grid(row=0, column=3, sticky=tk.NW, pady=10)
        self.description_l\
            .grid(row=1, column=0, sticky=tk.NE, padx=30)
        self.description_e.grid(row=1, column=1)

        self.is_nsfw\
            .grid_configure(row=1, column=2, sticky=tk.NW, padx=30)
        self.construct_meme_b\
            .grid(row=3, column=0, sticky=tk.E)

        self.image\
            .grid(row=3, column=1, sticky=tk.NW)
        # self.img_l\
        #     .grid(row=3, column=2, sticky=tk.NW)
        self.browse_img_b\
            .grid(row=3, column=3, sticky=tk.NW)

        self.run_b.grid(row=5, sticky=tk.E)

    def construct_meme(self) -> None:
        uname = self.username_e.get()
        password = self.password_e.get()
        description = self.description_e.get(1.0, "end")
        is_nsfw = True if self.nsfw_var.get() == 1 else False
        meme_file = self.meme_file if self.meme_file\
            else filedialog.askopenfile()

        self.constructed_meme = Meme(uname,
                                     password,
                                     description,
                                     str(meme_file),
                                     is_nsfw)
        self.popup("Success", "Meme was successfuly created!")

    def run(self) -> None:
        self.window.mainloop()

    def run_func(self) -> None:
        if not self.constructed_meme:
            self.popup("No meme", "Please create a meme first!")
            return
        self.get_connection()

    def ask_filename(self) -> None:
        self.meme_file = filedialog.askopenfilename()
        self.image.configure(text=os.path.split(self.meme_file)[1])

    def popup(self, title: str, msg: str) -> None:
        messagebox.showinfo(title=title, message=msg)

    def get_connection(self) -> None:
        toplevel = tk.Toplevel(self.window)
        toplevel.configure(bg=BG)

        ip_l = tk.Label(toplevel,
                        text="ip:",
                        bg=BG,
                        foreground=FG,
                        highlightbackground=BG,
                        activebackground=BLUE,
                        activeforeground=RED)
        port_l = tk.Label(toplevel,
                          text="port:",
                          bg=BG,
                          foreground=FG,
                          highlightbackground=BG,
                          activebackground=BLUE,
                          activeforeground=RED)
        ip_e = tk.Entry(toplevel,
                          bg=BG,
                          foreground=FG,
                          highlightbackground=BG)
        port_e = tk.Entry(toplevel,
                          bg=BG,
                          foreground=FG,
                          highlightbackground=BG)

        ip_l.grid(row=0, column=0)
        ip_e.grid(row=0, column=1)
        port_l.grid(row=1, column=0)
        port_e.grid(row=1, column=1)

        b = tk.Button(toplevel,
                      text="Confirm",
                      bg=BG,
                      foreground=FG,
                      highlightbackground=BG,
                      activebackground=BLUE,
                      activeforeground=RED,
                      command=lambda:
                      self.handle_popup(toplevel, [ip_e, port_e]))
        b.grid(row=2)

    def handle_popup(self, popup: tk.Toplevel,
                     entries: List[tk.Entry] = []) -> None:
        returns = [x.get() for x in entries]
        popup.destroy()
        self.popup_values = returns

        mtp = Mtp(self.popup_values[0],
                  int(self.popup_values[1]),
                  self.constructed_meme)
        mtp.run()
        self.popup("Status", mtp.get_status())


def main() -> None:
    gui = Gui()
    gui.run()


main()


if __name__ == "main":
    main()
