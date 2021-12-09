#! /usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox
from impl import Mtp, Meme

from typing import List, Optional


class Gui:
    def __init__(self) -> None:
        # main window
        self.window = tk.Tk()
        self.window.title("MTP Client")
        self.window.configure(bg="#282828")
        self.window.grid_rowconfigure(2, minsize=20)
        self.window.grid_rowconfigure(4, minsize=20)
        self.constructed_meme: Optional[Meme] = None

        # tkinter variables
        self.nsfw_var = tk.IntVar()

        # entries and checkboxes
        self.username_l = tk.Label(self.window, text="username: ")
        self.username_e = tk.Entry(self.window, bg="#404040")
        self.password_l = tk.Label(self.window, text="password: ")
        self.password_e = tk.Entry(self.window, bg="#404040")
        self.description_l = tk.Label(self.window, text="description: ")
        self.description_e = tk.Text(self.window,
                                     bg="#404040",
                                     width=15,
                                     height=3)
        self.is_nsfw = tk.Checkbutton(self.window,
                                      text="NSFW",
                                      onvalue=1,
                                      offvalue=0,
                                      variable=self.nsfw_var,
                                      bg="#404040")
        self.port_e = tk.Entry(self.window)
        self.ip_e = tk.Entry(self.window)

        # buttons
        self.construct_meme_b = tk.Button(self.window,
                                          text="CONSTRUCT MEME",
                                          command=self.construct_meme)
        self.run_b = tk.Button(self.window,
                               text="RUN",
                               command=self.run_func)
        self.image = tk.Label(self.window,
                              bg="#404040",
                              text="No meme chosen!")
        self.img_l = tk.Label(self.window, bg="#404040", text="choose a meme:")
        self.browse_img_b = tk.Button(self.window,
                                      text="BROWSE",
                                      command=self.ask_filename)

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
        self.img_l\
            .grid(row=3, column=2, sticky=tk.NW)
        self.browse_img_b\
            .grid(row=3, column=3, sticky=tk.NW)

        self.run_b.grid(row=5, sticky=tk.E)

    def construct_meme(self) -> None:
        uname = self.username_e.get()
        password = self.password_e.get()
        description = self.description_e.get(1.0, "end")
        is_nsfw = True if self.nsfw_var == 1 else False
        print(is_nsfw)
        meme_file = self.meme_file if self.meme_file\
            else filedialog.askopenfile()

        self.constructed_meme = Meme(uname,
                                     password,
                                     description,
                                     str(meme_file),
                                     is_nsfw)

    def run(self) -> None:
        self.window.mainloop()

    def run_func(self) -> None:
        if not self.constructed_meme:
            self.popup("No meme", "Please create a meme first!")
            return
        self.get_connection()

    def ask_filename(self) -> None:
        self.meme_file = filedialog.askopenfilename()
        self.image.configure(text=self.meme_file)

    def popup(self, title: str, msg: str) -> None:
        messagebox.showinfo(title=title, message=msg)

    def get_connection(self) -> None:
        toplevel = tk.Toplevel(self.window)

        ip_l = tk.Label(toplevel, text="ip:")
        port_l = tk.Label(toplevel, text="port:")
        ip_e = tk.Entry(toplevel)
        port_e = tk.Entry(toplevel)

        ip_l.grid(row=0, column=0)
        ip_e.grid(row=0, column=1)
        port_l.grid(row=1, column=0)
        port_e.grid(row=1, column=1)

        b = tk.Button(toplevel,
                      text="Confirm",
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
        print(str(mtp))


def main() -> None:
    gui = Gui()
    gui.run()


main()


if __name__ == "main":
    main()
