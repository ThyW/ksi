import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Optional
from flask import url_for

from dataclasses import dataclass
from dataclasses_json import dataclass_json

DEVICES_FOLDER = 'devices'


def current_timestamp() -> int:
    return int(datetime.now().timestamp())


class DeviceType(Enum):
    PLUG = "SmartPlug"
    LIGHT = "SmartLight"
    RADIATOR = "SmartRadiator"
    TEMPERATURE = "TemperatureSensor"
    SWITCH = "SwitchSensor"
    MOTION = "MotionSensor"


@dataclass_json
@dataclass
class GenericDevice:
    type: DeviceType
    id: str = None
    notes: str = ""

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())


@dataclass
class DeviceWithOnOffTracking(GenericDevice):
    current_state: bool = False
    power_usage_last_recalculated: int = 0
    power_usage: int = 0
    power_usage_coefficient: int = 100

    def recalculate_cost(self):
        ts = current_timestamp()
        if self.current_state:
            time_diff = (ts - self.power_usage_last_recalculated)
            self.power_usage += int(time_diff * self.power_usage_coefficient / 100)
        self.power_usage_last_recalculated = ts
        save_device(self)


@dataclass
class SmartPlug(DeviceWithOnOffTracking):
    type: DeviceType = DeviceType.PLUG


@dataclass
class SmartLight(DeviceWithOnOffTracking):
    type: DeviceType = DeviceType.LIGHT
    color_temperature: int = 5000


@dataclass
class SmartRadiator(DeviceWithOnOffTracking):
    type: DeviceType = DeviceType.RADIATOR


@dataclass
class EventPushSensor(GenericDevice):
    collector_url: str = None

    def __post_init__(self):
        GenericDevice.__post_init__(self)
        if self.collector_url is None:
            try:
                # maybe create Public Request bin? https://requestbin.com/r
                self.collector_url = url_for("incoming_event", device_id=self.id, _external=True)
            except RuntimeError:
                self.collector_url = f'https://example.com/ksi?id={self.id}'
                print("[~] Flask is not available, to create incomming event URL. Using example.com instead.")


@dataclass
class TemperatureSensor(GenericDevice):
    type: DeviceType = DeviceType.TEMPERATURE
    temperature: float = 20


@dataclass
class MotionSensor(EventPushSensor):
    type: DeviceType = DeviceType.MOTION
    last_triggered_timestamp: int = 0


@dataclass
class SwitchSensor(EventPushSensor, DeviceWithOnOffTracking):
    type: DeviceType = DeviceType.SWITCH


def save_device(device: GenericDevice) -> GenericDevice:
    Path(f'{DEVICES_FOLDER}/').mkdir(parents=True, exist_ok=True)
    with open(f"{DEVICES_FOLDER}/{device.id}.json", "w", encoding="utf8") as f:
        f.write(device.to_json(indent=4))
    return device


def load_device(device_id: str) -> Optional[GenericDevice]:
    try:
        with open(f"{DEVICES_FOLDER}/{device_id}.json", "r", encoding="utf8") as f:
            content = f.read()
    except FileNotFoundError:
        return None
    device = GenericDevice.from_json(content)
    return type_to_class[device.type].from_json(content)


known_classes = [SmartLight, SmartPlug, SmartRadiator, MotionSensor, SwitchSensor, TemperatureSensor]
type_to_class = dict([(x.type, x) for x in known_classes])
