#!/usr/bin/env python3
from typing import List, Dict
from enum import Enum
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from json import loads


class DeviceType(Enum):
    MOTION_SENSOR = "MotionSensor"
    SMART_LIGHT = "SmartLight"
    SMART_PLUG = "SmartPlug"
    SMART_RADIATOR = "SmartRadiator"
    SWITCH_SENSOR = "SwitchSensor"
    TEMPERATURE_SENSOR = "TemperatureSensor"


@dataclass_json
@dataclass
class DeviceData:
    id: str
    notes: str
    actions: Dict[str, str]


@dataclass
class DevicePowerData(DeviceData):
    current_state: bool
    power_usage: int
    power_usage_coefficient: int
    power_usage_last_recalculated: int
