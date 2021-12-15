#!/usr/bin/env python3
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import uuid
import json
from typing import Optional


PATH = "users/"
USERS_FILE = f"{PATH}db.txt"


@dataclass_json
@dataclass
class Roommate:
    uname: str
    passwd: str
    id: int
    costs: int = 0
    time: int = 0

    @classmethod
    def new(cls, uname: str, passwd: str) -> "Roommate":
        id = uuid.uuid4()
        c = Roommate(uname, passwd, int(id))
        return c


def save_roommate(r: Roommate) -> None:
    with open(USERS_FILE, "r+") as f:
        if str(r.id) in f.readlines():
            return
        f.write(f"{r.uname}:{str(r.id)}\n")

    with open(f"{PATH}{str(r.id)}", "w") as f2:
        f2.write(r.to_json())

def load_roommate(name: str) -> Optional[Roommate]:
    with open(USERS_FILE, "r") as uf:
        for each in uf.readlines():
            sp = each.split(':')
            if sp[0] == name: 
                fname = sp[1].strip()
                with open(f"{PATH}{fname}", "r") as file:
                    return Roommate.from_json(file.read())
