#!/usr/bin/env python3

from device import DevicePowerData, DeviceType, DeviceData
from json import loads
from dataclasses import dataclass
from dataclasses_json import dataclass_json

#  TODO: finish all the class methods

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


def test() -> None:
    switch_json = """
{
  "actions": {
    "change_report_url": "http://home_automation.iamroot.eu/device/6be66bc8-2d69-4fad-ba29-672f11e4844c/report_url?url=http%3A%2F%2Fhome_automation.iamroot.eu%2Fdevice%2F6be66bc8-2d69-4fad-ba29-672f11e4844c%2Fevent", 
    "device_info": "http://home_automation.iamroot.eu/device/6be66bc8-2d69-4fad-ba29-672f11e4844c", 
    "set_notes_POST": "http://home_automation.iamroot.eu/device/6be66bc8-2d69-4fad-ba29-672f11e4844c/notes", 
    "trigger_report": "http://home_automation.iamroot.eu/device/6be66bc8-2d69-4fad-ba29-672f11e4844c/trigger"
  }, 
  "collector_url": "http://home_automation.iamroot.eu/device/6be66bc8-2d69-4fad-ba29-672f11e4844c/event", 
  "current_state": false, 
  "id": "6be66bc8-2d69-4fad-ba29-672f11e4844c", 
  "notes": "", 
  "power_usage": 0, 
  "power_usage_coefficient": 100, 
  "power_usage_last_recalculated": 1639599062, 
  "type": "SwitchSensor"
}"""
    switch = SwitchSensor.from_json(switch_json)
    print(switch)
test()
