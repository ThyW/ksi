#!/usr/bin/env python3
from typing import List
from enum import Enum

from json import loads


class DeviceType(str, Enum):
    MotionSensor = "MotionSensor"
    SmartLight = "SmartLight"
    SmartPlug = "SmartPlug"
    SmartRadiator = "SmartRadiator"
    SmartSwitch = "SmartSwitch"
    TemperatureSensor = "TemperatureSensor"


class Device:
    def __init__(self, type_: DeviceType, id: str, notes: str):
        self.type: DeviceType = type_
        self.id: str = id
        self.notes: str = notes
        self.actions: List[str] = []

    def get_type(self) -> str:
        return self.type

    def get_id(self) -> str:
        return self.id

    def get_notes(self) -> str:
        return self.notes

    def get_actions(self) -> List[str]:
        return self.actions

    def add_actions(self, a: List[str]) -> None:
        [self.actions.append(x) for x in a]

    def add_notes(self, s: str) -> None:
        self.notes += s

    @classmethod
    def from_json(cls, json_obj: str) -> "Device":
        o = loads(json_obj)

        actions = [v for v in o['actions'].values()]
        d = Device(o['type'], o['id'], o['notes'])
        d.add_actions(actions)
        return d

    def __str__(self) -> str:
        r = f"Device: id: {self.get_id()}, type: {self.get_type()}, notes: {self.get_notes()}, actions: {[x for x in self.get_actions()]}"
        return r
