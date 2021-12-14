#!/usr/bin/env python3
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass
@dataclass_json
class Roommate:
    name: str
    uname: str
    passwrd: str
    costs: int
    time: int
