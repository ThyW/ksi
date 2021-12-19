#!/usr/bin/env python3

from device import DevicePowerData, DeviceType, DeviceData
from json import loads
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Union


@dataclass
class MotionSensor(DeviceData):
    collector_url: str
    last_triggered_timestamp: int
    type: DeviceType = DeviceType.MOTION_SENSOR


@dataclass
class SmartLight(DevicePowerData):
    color_temperature: int
    type: DeviceType = DeviceType.SMART_LIGHT


@dataclass
class SwitchSensor(DevicePowerData):
    collector_url: str
    type: DeviceType = DeviceType.SWITCH_SENSOR


@dataclass
class SmartPlug(DevicePowerData):
    type: DeviceType = DeviceType.SMART_PLUG


@dataclass
class SmartRadiator(DevicePowerData):
    type: DeviceType = DeviceType.SMART_RADIATOR


@dataclass
class TemperatureSensor(DevicePowerData):
    temperature: int
    type: DeviceType = DeviceType.TEMPERATURE_SENSOR


Device = Union[SmartLight, SwitchSensor, MotionSensor]
