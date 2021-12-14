#!/usr/bin/env python3

from device import Device, DeviceType
from json import loads

#  TODO: finish all the class methods

class MotionSensor(Device):
    def __init__(self, type_: DeviceType, id: str, notes: str) -> None:
        super().__init__(type_, id, notes)
        self.collector_url: str
        self.last_triggered_timestamp: int = 0

    @classmethod
    def from_json(cls, json_obj: str) -> "MotionSensor":
        o = loads(json_obj)

        d = MotionSensor(o['type'], o['id'], o['notes'])
        d.add_actions([x for x in o['actions']])
        d.collector_url = o['collector_url']
        d.last_triggered_timestamp = o['last_triggered_timestamp']
        return d


class SmartLight(Device):
    def __init__(self, type_: DeviceType, id: str, notes: str) -> None:
        super().__init__(type_, id, notes)
        self.color_temperature: int
        self.current_state: bool
        self.power_usage: int
        self.power_usage_coefficient: int
        self.power_usage_last_recalculated: int

    @classmethod
    def from_json(cls, json_obj: str) -> "SmartLight":
        o = loads(json_obj)

        d = SmartLight(o['type'], o['id'], o['notes'])
        d.add_actions([x for x in o['actions']])
        d.color_temperature = o['color_temperature']
        d.current_state = o['current_state']
        d.power_usage = o['power_usage']
        d.power_usage_coefficient = o['power_usage_coefficient']
        d.power_usage_last_recalculated = o['power_usage_last']
        return d


class SmartPlug(Device):
    def __init__(self, type_: DeviceType, id: str, notes: str) -> None:
        super().__init__(type_, id, notes)
        self.current_state: bool
        self.power_usage: int
        self.power_usage_coefficient: int
        self.power_usage_last_recalculated: int

    @classmethod
    def from_json(cls, json_obj: str) -> "SmartPlug":
        o = loads(json_obj)

        d = SmartPlug(o['type'], o['id'], o['notes'])
        d.add_actions([x for x in o['actions']])
        d.current_state = o['current_state']
        d.power_usage = o['power_usage']
        d.power_usage_coefficient = o['power_usage_coefficient']
        d.power_usage_last_recalculated = o['power_usage_last_recalculated']
        return d


class SmartRadiator(Device):
    def __init__(self, type_: DeviceType, id: str, notes: str) -> None:
        super().__init__(type_, id, notes)
        self.current_state: bool
        self.power_usage: int
        self.power_usage_coefficient: int
        self.power_usage_last_recalculated: int

    @classmethod
    def from_json(cls, json_obj: str) -> "SmartRadiator":
        o = loads(json_obj)

        d = SmartRadiator(o['type'], o['id'], o['notes'])
        d.add_actions([x for x in o['actions']])
        d.current_state = o['current_state']
        d.power_usage = o['power_usage']
        d.power_usage_coefficient = o['power_usage_coefficient']
        d.power_usage_last_recalculated = o['power_usage_last_recalculated']
        return d

class SwitchSensor(Device):
    def __init__(self, type_: DeviceType, id: str, notes: str) -> None:
        super().__init__(type_, id, notes)
        self.current_state: bool
        self.power_usage: int
        self.power_usage_coefficient: int
        self.power_usage_last_recalculated: int

    @classmethod
    def from_json(cls, json_obj: str) -> "SmartRadiator":
        o = loads(json_obj)

        d = SwitchSensor(o['type'], o['id'], o['notes'])
        d.add_actions([x for x in o['actions']])
        d.current_state = o['current_state']
        d.power_usage = o['power_usage']
        d.power_usage_coefficient = o['power_usage_coefficient']
        d.power_usage_last_recalculated = o['power_usage_last_recalculated']
        return d

class TemperatureSensor(Device):
    def __init__(self, type_: DeviceType, id: str, notes: str) -> None:
        super().__init__(type_, id, notes)
        self.temperature: int

    @classmethod
    def from_json(cls, json_obj: str) -> "TemperatureSensor":
        o = loads(json_obj)

        d = SwitchSensor(o['type'], o['id'], o['notes'])
        d.add_actions([x for x in o['actions']])
        d.temperature = o['temperature']
        return d
