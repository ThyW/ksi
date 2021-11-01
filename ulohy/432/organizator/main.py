#!/usr/bin/env python3

from typing import List, Optional, Dict, Tuple
import time
from datetime import datetime, date as dt
import re
import tkinter
from tkinter import ttk, filedialog
import json
from sys import argv


class Contact:
    def __init__(self, name: str,
                 email: str = "",
                 phone_number: str = "",
                 birthday: str = "",
                 note: str = ""
                 ) -> None:
        self.name: str = name.strip()
        if self.check_mail(email):
            self.email = email
        else:
            self.email = "none"
        if self.check_birthday(birthday):
            self.birthday = birthday
        else:
            self.birthday = "none"
        if self.check_phone(phone_number):
            self.phone_number = phone_number
        else:
            self.phone_number = "none"
        if note:
            self.note: str = note
        else:
            self.note = "none"

    @classmethod
    def check_mail(cls, expression: str) -> bool:
        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                    expression):
            return True
        return False

    @classmethod
    def check_birthday(cls, expression: str) -> bool:
        dt: Optional[time.struct_time] = None
        try:
            dt = time.strptime(expression, "%d.%m.%Y")
            if dt:
                return True
        except ValueError:
            return False

        return False

    @classmethod
    def check_phone(cls, expression: str) -> bool:
        for i, each in enumerate(expression):
            if (i != 0 and each == "+") and not each.isdigit() and each != " ":
                return False
        return True

    def edit(self, args: Dict[str, str]) -> None:
        if args["name"]:
            self.name = args["name"]
        if args["note"]:
            self.note = args["note"]
        if args["email"]:
            if Contact.check_mail(args["email"]):
                self.email = args["email"]
        if args["phone_number"]:
            if Contact.check_phone(args["phone_number"]):
                self.phone_number = args["phone_number"]
        if args["birthday"]:
            if Contact.check_birthday(args["birthday"]):
                self.birthday = args["birthday"]

    def __str__(self) -> str:
        s = ""
        s += self.name + "\n"
        s += self.email + "\n"
        s += self.phone_number + "\n"
        s += self.birthday + "\n"
        s += self.note + "\n"
        return s

    def parse(self) -> Tuple[str, Dict[str, str]]:
        return (self.name, {
            "email": self.email,
            "phone_number": self.phone_number,
            "note": self.note,
            "birthday": self.birthday,
            })


class Gui:
    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.window.title("Organizator")
        self.window.geometry("800x600")

        # frame
        self.frame = tkinter.Frame(self.window)
        self.frame.pack(fill=tkinter.BOTH, expand=1)

        # treeview and scrollbar
        self.treeframe = tkinter.Frame(self.window)
        self.treeframe.pack(pady=20)

        self.tvscrollbar = ttk.Scrollbar(self.treeframe,
                                         orient=tkinter.VERTICAL)
        self.tvscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.treeview = ttk.Treeview(self.treeframe,
                                     columns=("1", "2", "3", "4", "5"),
                                     show="headings",
                                     height=8,
                                     yscrollcommand=self.tvscrollbar.set)
        self.tvscrollbar.configure(command=self.treeview.yview)
        self.treeview.pack()
        self.treeview.heading("1", text="name")
        self.treeview.heading("2", text="email")
        self.treeview.heading("3", text="phone_number")
        self.treeview.heading("4", text="birthday")
        self.treeview.heading("5", text="note")

        # buttons
        self.add_contact_button = tkinter.Button(self.window,
                                                 text="Add Contact",
                                                 command=self.add_contact)
        self.remove_contact_button = tkinter.Button(self.window,
                                                    text="Remove Contact",
                                                    command=self.remove_contact
                                                    )
        self.search_contact_button = tkinter.Button(self.window,
                                                    text="Search Contact",
                                                    command=self.search_contact
                                                    )
        self.load_contacts_button = tkinter.Button(self.window,
                                                   text="Load Contacts",
                                                   command=self.load_contacts)
        self.edit_contact_button = tkinter.Button(self.window,
                                                  text="Edit Contacts",
                                                  command=self.edit_contact)
        self.save_contacts_button = tkinter.Button(self.window,
                                                   text="Save contacts",
                                                   command=self.save_contacts)
        self.clear_search_button = tkinter.Button(self.window,
                                                  text="clear search",
                                                  command=self.clear_search)
        self.sort_button = tkinter.Button(self.window,
                                          text="sort",
                                          command=self.sort)
        self.show_button = tkinter.Button(self.window,
                                          text="show only",
                                          command=self.make_show)

        # packs
        self.add_contact_button.pack()
        self.remove_contact_button.pack()
        self.edit_contact_button.pack()
        self.search_contact_button.pack()
        self.clear_search_button.pack()
        self.load_contacts_button.pack()
        self.save_contacts_button.pack()
        self.sort_button.pack()
        self.show_button.pack()

    def run(self, org: "Organizator") -> None:
        self.org = org
        self.make_notify(self.org.contacts)
        self.window.mainloop()

    def clear_search(self) -> None:
        self.display_contacts()

    def add_contact(self) -> None:
        # self.make_window("new")
        # TODO
        self.make_window("new_contact")

    def add_contact_callback(self, window: tkinter.Toplevel,
                             entries: Tuple[tkinter.Entry, ...]) -> None:
        values = []
        values = [x.get() for x in entries]
        if not values[0]:
            self.make_error("One of the required entries was empty!")
        c = Contact(values[0], values[1], values[2], values[3], values[4])
        self.org.add_contact(c)
        self.display_contacts()
        window.destroy()

    def remove_contact(self) -> None:
        selected = self.treeview.selection()
        for each in selected:
            values = self.treeview.item(each, "value")
            self.org.remove_contact(values[0])
            self.treeview.delete(each)

    def load_contacts(self) -> None:
        self.org.load_contacts(filedialog
                               .askopenfilename(defaultextension=".json"))
        self.display_contacts()
        self.make_notify(self.org.notify_birthday())

    def save_contacts(self) -> None:
        self.org.save_contacts(filedialog
                               .asksaveasfilename())

    def edit_contact(self) -> None:
        selected = self.treeview.selection()
        index = int(selected[0][1:]) - 1
        self.edited = self.org.contacts[index]
        self.make_window("edit_contact")

    def edit_callback(self,
                      window: tkinter.Toplevel,
                      entries: Tuple[tkinter.Entry, ...]) -> None:
        values = []
        values = [x.get() for x in entries]
        value_dict = {
                "name": values[0],
                "email": values[1],
                "phone_number": values[2],
                "birthday": values[3],
                "note": values[4]
                }
        self.org.edit_contact(self.edited, value_dict)
        self.display_contacts()
        window.destroy()

    def search_contact(self) -> None:
        self.make_search()

    def search_fallback(self,
                        window: tkinter.Toplevel,
                        entry: tkinter.Entry) -> None:
        value = []
        value = entry.get()
        searches = self.org.search_contacts(value)

        self.display_contacts(contacts=searches)
        self.make_error("Some values were not parsed!")
        window.destroy()

    def sort(self) -> None:
        self.make_sort()

    def sort_callback(self, window: tkinter.Toplevel, type: str) -> None:
        window.destroy()
        if type == "a":
            self.org.contacts.sort(key=lambda x: x.name.lower())
        if type == "z":
            self.org.contacts.sort(key=lambda x: x.name.lower())
            self.org.contacts.reverse()
        self.display_contacts()

    def display_contacts(self,
                         contacts: Optional[List[Contact]] = None) -> None:
        self.treeview.delete(*self.treeview.get_children())
        if not contacts:
            for each in self.org.contacts:
                values = (each.name,
                          each.email,
                          each.phone_number,
                          each.birthday,
                          each.note)
                self.treeview.insert("", "end", iid=None, values=values)
        else:
            for each in contacts:
                values = (each.name,
                          each.email,
                          each.phone_number,
                          each.birthday,
                          each.note)
                self.treeview.insert("", "end", iid=None, values=values)

    def make_search(self) -> None:
        toplevel = tkinter.Toplevel()

        label = tkinter.Label(toplevel, text="search name")
        entry = tkinter.Entry(toplevel)

        label.pack()
        entry.pack()

        button = tkinter.Button(toplevel,
                                text="Subtmit",
                                command=lambda:
                                self.search_fallback(toplevel,
                                                     entry))
        button.pack()

    def make_window(self, type: str) -> None:
        toplevel = tkinter.Toplevel()

        lable_name = tkinter.Label(toplevel, text="name")
        lable_phone = tkinter.Label(toplevel, text="phone number")
        lable_bday = tkinter.Label(toplevel, text="birthday")
        lable_mail = tkinter.Label(toplevel, text="email")
        lable_note = tkinter.Label(toplevel, text="note")

        entry_name = tkinter.Entry(toplevel)
        entry_mail = tkinter.Entry(toplevel)
        entry_phone = tkinter.Entry(toplevel)
        entry_bday = tkinter.Entry(toplevel)
        entry_note = tkinter.Entry(toplevel)

        lable_name.pack()
        entry_name.pack()
        lable_mail.pack()
        entry_mail.pack()
        lable_phone.pack()
        entry_phone.pack()
        lable_bday.pack()
        entry_bday.pack()
        lable_note.pack()
        entry_note.pack()

        entries = (entry_name, entry_mail, entry_phone, entry_bday,
                   entry_note)

        if type == "new_contact":
            button = tkinter.Button(toplevel,
                                    text="Subtmit",
                                    command=lambda:
                                    self.add_contact_callback(toplevel,
                                                              entries))
            button.pack()
        if type == "edit_contact":
            button = tkinter.Button(toplevel,
                                    text="Subtmit",
                                    command=lambda:
                                    self.edit_callback(toplevel,
                                                       entries))
            button.pack()

    def make_error(self, msg: str) -> None:
        window = tkinter.Toplevel()
        t = tkinter.Label(window, text=msg)
        t.pack()
        button = tkinter.Button(window,
                                text="Ok",
                                command=lambda: window.destroy())
        button.pack()

    def make_sort(self) -> None:
        window = tkinter.Toplevel()

        button = tkinter.Button(window,
                                text="A-Z",
                                command=lambda:
                                self.sort_callback(window, "a"))
        button.pack()
        button1 = tkinter.Button(window,
                                 text="Z-A",
                                 command=lambda:
                                 self.sort_callback(window, "z"))
        button1.pack()

    def make_notify(self, cs: List[Contact]) -> None:
        if cs:
            window = tkinter.Toplevel()
            for each in cs:
                label = tkinter.Label(window,
                                      text=f"{each.name} has birthday today!")
                label.pack()
            button = tkinter.Button(window,
                                    text="Ok",
                                    command=lambda: window.destroy())
            button.pack()

    def show_only(self, s: str) -> None:
        self.treeview.delete(*self.treeview.get_children())
        if s == "name":
            for each in self.org.contacts:
                values = (each.name, "", "", "", "")
                self.treeview.insert("", tkinter.END, values=values)
        if s == "email":
            for each in self.org.contacts:
                values = ("", each.email, "", "", "")
                self.treeview.insert("", tkinter.END, values=values)

        if s == "phone":
            for each in self.org.contacts:
                values = ("", "", each.phone_number, "", "")
                self.treeview.insert("", tkinter.END, values=values)
        if s == "birthday":
            for each in self.org.contacts:
                values = ("", "", "", each.birthday, "")
                self.treeview.insert("", tkinter.END, values=values)
        if s == "note":
            for each in self.org.contacts:
                values = ("", "", "", "", each.note)
                self.treeview.insert("", tkinter.END, values=values)

    def make_show(self) -> None:
        toplevel = tkinter.Toplevel()

        button1 = tkinter.Button(toplevel,
                                 text="name",
                                 command=lambda:
                                 self.show_only("name"))
        button2 = tkinter.Button(toplevel,
                                 text="email",
                                 command=lambda:
                                 self.show_only("email"))
        button3 = tkinter.Button(toplevel,
                                 text="phone",
                                 command=lambda:
                                 self.show_only("phone"))
        button4 = tkinter.Button(toplevel,
                                 text="bday",
                                 command=lambda:
                                 self.show_only("birthday"))
        button5 = tkinter.Button(toplevel,
                                 text="note",
                                 command=lambda:
                                 self.show_only("note"))
        button6 = tkinter.Button(toplevel,
                                 text="all",
                                 command=lambda:
                                 self.display_contacts())
        button7 = tkinter.Button(toplevel,
                                 text="close",
                                 command=lambda:
                                 toplevel.destroy())
        button1.pack()
        button2.pack()
        button3.pack()
        button4.pack()
        button5.pack()
        button6.pack()
        button7.pack()


class Organizator:
    def __init__(self, gui=False) -> None:
        self.contacts: List[Contact] = list()
        if gui:
            self.gui: Gui = Gui()

    def load_contacts(self, filename: str) -> None:
        self.contacts.clear()
        with open(filename, "r") as file:
            raw_json: Dict = json.loads(file.read())
            for (key, value) in raw_json.items():
                self.contacts.append(Contact(key,
                                     email=value["email"],
                                     phone_number=value["phone_number"],
                                     birthday=value["birthday"],
                                     note=value["note"]))
            file.close()

    def save_contacts(self, filename: str) -> None:
        d = dict()
        for each in self.contacts:
            parsed = each.parse()
            d[parsed[0]] = parsed[1]
        with open(filename, "w") as file:
            json.dump(d, file)
            file.close()

    def add_contact(self, contact: Contact) -> None:
        self.contacts.append(contact)

    def remove_contact(self, name: str) -> None:
        for each in self.contacts:
            if each.name == name:
                del each
            return

    def edit_contact(self, contact: Contact, args: Dict[str, str]) -> None:
        contact.edit(args)

    def notify_birthday(self) -> List[Contact]:
        dates: List[Tuple[time.struct_time, Contact]] = \
                [(time.strptime(x.birthday, "%d.%m.%Y"), x)
                 for x in self.contacts]
        today = dt.today()
        bdays: List[Contact] = list()
        for date, contact in dates:
            timestamp = datetime.fromtimestamp(time.mktime(date))
            timestr = f"{timestamp.year}-{timestamp.month}-{timestamp.day}"
            if timestr == str(today):
                bdays.append(contact)
        return bdays

    def search_contacts(self, name: str) -> List[Contact]:
        list: List[Contact] = []
        for each in self.contacts:
            if each.name == name or each.name.startswith(name):
                list.append(each)

        return list


def contact_test() -> None:
    # check phone numbers, emails and bdays
    assert Contact.check_phone("+421111111111")
    assert Contact.check_phone("421111111111")
    assert Contact.check_phone("421 111 1111 11")
    assert Contact.check_mail("dvere@dvere.com")
    assert Contact.check_birthday("1.1.1970")
    assert Contact.check_birthday("1.11.2011")
    print("contact_test() done.")


def gui_test() -> None:
    gui: Gui = Gui()
    org: Organizator = Organizator()
    gui.run(org)

    print("guit_test() done.")


def organizator_test() -> None:
    org = Organizator()
    org.load_contacts("contacts.json")
    org.notify_birthday()

    print("organizator_test() done.")


def main() -> None:
    gui = Gui()
    org = Organizator()
    gui.run(org)
    pass


def tests() -> None:
    contact_test()
    gui_test()
    organizator_test()
    pass


if __name__ == '__main__':
    main()


if "-test" in argv:
    tests()
