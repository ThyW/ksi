from flask import Flask, json, request, url_for, redirect, Response
from typing import List, Tuple, Optional, Union
from time import sleep
import json
import urllib.parse
import requests
from devices_offline import *


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Lower-case version of the states
STATE_ON = 'on'
STATE_OFF = 'off'


def error_msg(msg: str = "Unknown error", status=500):
    return {"error": msg}, status


def links(device: GenericDevice) -> dict:
    answer = {}
    type: Union[str, DeviceType] = device.type

    answer["device_info"] = f'{url_for("device_endpoint", device_id=device.id, _external=True)}'
    answer["set_notes_POST"] = f'{url_for("set_notes", device_id=device.id, _external=True)}'
    
    if type in [DeviceType.LIGHT, DeviceType.PLUG]:
        # answer["power_usage"] = f'{url_for("power_usage", device_id=device.id, _external=True)}'
        answer["turn_on"] = f'{url_for("change_state", device_id=device.id, state=STATE_ON, _external=True)}'
        answer["turn_off"] = f'{url_for("change_state", device_id=device.id, state=STATE_OFF, _external=True)}'
    
    if type == DeviceType.LIGHT:
        answer["change_color_sunset"] = f'{url_for("change_color", device_id=device.id, color_temperature=3500, _external=True)}'
        answer["change_color_high_noon"] = f'{url_for("change_color", device_id=device.id, color_temperature=5000, _external=True)}'
        answer["change_color_blue_sky"] = f'{url_for("change_color", device_id=device.id, color_temperature=10000, _external=True)}'
        answer["toggle_state"] = f'{url_for("toggle_state", device_id=device.id, _external=True)}'

    if type == DeviceType.RADIATOR:
        answer["change_intensity_0_percent"] = f'{url_for("change_intensity", device_id=device.id, intensity=0, _external=True)}'
        answer["change_intensity_50_percent"] = f'{url_for("change_intensity", device_id=device.id, intensity=50, _external=True)}'
        answer["change_intensity_100_percent"] = f'{url_for("change_intensity", device_id=device.id, intensity=100, _external=True)}'

    if isinstance(device, EventPushSensor):
        encoded_url_arg = urllib.parse.urlencode({'url': device.collector_url})
        answer["change_report_url"] = f'{url_for("change_report_url", device_id=device.id, _external=True)}?{encoded_url_arg}'
        answer["trigger_report"] = url_for("trigger_report", device_id=device.id, _external=True)

    if type == DeviceType.TEMPERATURE:
        answer["set_fake_temperature_0_C"] = url_for("set_fake_temperature", device_id=device.id, temperature=0, _external=True)
        answer["set_fake_temperature_20_C"] = url_for("set_fake_temperature", device_id=device.id, temperature=20, _external=True)
        answer["set_fake_temperature_0_K"] = url_for("set_fake_temperature", device_id=device.id, temperature=-273.15, _external=True)

    return answer


def save_and_return_device(device) -> str:
    save_device(device)
    return device_endpoint(device.id)


def save_and_redirect_to_device(device) -> Response:
    save_device(device)
    return redirect(url_for("device_endpoint", device_id=device.id, _external=True), code=302)


@app.route("/newSmartLight")
def new_smart_light():
    return save_and_return_device(SmartLight())


@app.route("/newSmartPlug")
def new_smart_plug():
    return save_and_return_device(SmartPlug())


@app.route("/newSmartRadiator")
def new_smart_radiator():
    return save_and_return_device(SmartRadiator())


@app.route("/newTemperatureSensor")
def new_temperature_sensor():
    return save_and_return_device(TemperatureSensor())


@app.route("/newMotionSensor")
def new_motion_sensor():
    return save_and_return_device(MotionSensor())


@app.route("/newSwitchSensor")
def new_switch_sensor():
    return save_and_return_device(SwitchSensor())


@app.route("/device/<device_id>")
def device_endpoint(device_id: str):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)
    
    if getattr(device, "recalculate_cost", None) is not None:
        device.recalculate_cost()

    answer = json.loads(device.to_json())  # This is a hack because dataclasses_json.to_json knows how to handle Enums, while json.dumps doesn't.
    answer["actions"] = links(device)
    return answer


@app.route("/device/<device_id>/state/<state>", methods=["GET", "POST"])
def change_state(device_id: str, state: str):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)

    state = state.lower()
    if state not in [STATE_ON, STATE_OFF, "true", "false"]:
        return error_msg("Unknown state", 400)
    if getattr(device, "current_state", None) is None:
        return error_msg("This device doesn't have a state", 400)

    if isinstance(device, DeviceWithOnOffTracking):
        device.recalculate_cost()
    
    if state in [STATE_ON, "true"]:
        device.current_state = True
    if state in [STATE_OFF, "false"]:
        device.current_state = False

    return save_and_return_device(device)


@app.route("/device/<device_id>/toggle", methods=["GET", "POST"])
def toggle_state(device_id: str):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)
    if getattr(device, "current_state", None) is None:
        return error_msg("This device doesn't have a state", 400)
    
    if isinstance(device, DeviceWithOnOffTracking):
        device.recalculate_cost()
    
    # Fix for bug from 19.11.2021
    state = str(device.current_state).lower()
    if state == STATE_ON:
        device.current_state = True
    elif state == STATE_OFF:
        device.current_state = False

    device.current_state = not device.current_state

    return save_and_return_device(device)


@app.route("/device/<device_id>/intensity/<intensity>", methods=["GET", "POST"])
def change_intensity(device_id: str, intensity: int):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)
    if not isinstance(device, SmartRadiator):
        return error_msg("This device doesn't have an intensity", 400)
    
    try:
        intensity_int = int(intensity)
    except ValueError:
        return error_msg("Intensity is not convertible to int.", 400)

    if not(0 <= intensity_int <= 100):
        return error_msg("Intensity is not in the allowed range.", 400)

    device.recalculate_cost()
    device.intensity = intensity_int
    return save_and_return_device(device)


@app.route("/device/<device_id>/color_temperature/<color_temperature>", methods=["GET", "POST"])
def change_color(device_id: str, color_temperature: int):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)
    if getattr(device, "color_temperature", None) is None:
        return error_msg("This device doesn't have a color temperature", 400)
    
    try:
        color_temp_int = int(color_temperature)
    except ValueError:
        return error_msg("Color temperature is not convertable to int", 400)

    if not(1000 <= color_temp_int <= 15000):
        return error_msg("Color temperature is outside of allowable range.", 400)

    device.color_temperature = color_temp_int
    return save_and_return_device(device)


@app.route("/device/<device_id>/report_url", methods=["GET", "POST"])
def change_report_url(device_id: str):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)
    if getattr(device, "collector_url", None) is None:
        return error_msg("This device doesn't have a collector url", 400)

    url_encoded = request.args.get('url')
    # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.quote_plus

    url = urllib.parse.unquote_plus(url_encoded)
    device.collector_url = url
    return save_and_return_device(device)


@app.route("/device/<device_id>/trigger", methods=["GET", "POST"])
def trigger_report(device_id: str):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)
    if getattr(device, "collector_url", None) is None:
        return error_msg("This device doesn't have a collector url", 400)

    if getattr(device, "last_triggered_timestamp", None) is not None:
        device.last_triggered_timestamp = current_timestamp()
        save_device(device)

    device_information = device_endpoint(device_id)
    resp = requests.post(device.collector_url, data=device_information, headers={'Content-type': 'application/json'})
    device_information['collector_response'] = {'data': str(resp.content), 'status_code': resp.status_code}
    return device_information


@app.route("/device/<device_id>/event", methods=["POST"])
def incoming_event(device_id: str):
    device = load_device(device_id)
    print(f"INCOMING EVENT from {device_id} with data len {len(request.data)}")
    return save_and_return_device(device)


@app.route("/")
def homepage():
    new_device_endpoints = ["new_smart_light", "new_smart_plug", "new_smart_radiator", "new_temperature_sensor", "new_motion_sensor", "new_switch_sensor"]
    answer = {}
    for x in new_device_endpoints:
        answer[x] = url_for(x, _external=True)
    answer["device_info"] = url_for("device_endpoint", device_id="_id_", _external=True)
    return answer


@app.route("/device/<device_id>/fake_temperature/<temperature>", methods=["GET", "POST"])
def set_fake_temperature(device_id: str, temperature: float):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)
    if getattr(device, "temperature", None) is None:
        return error_msg("This device doesn't have a temperature", 400)

    try:
        temperature_float = float(temperature)
    except ValueError:
        return error_msg("Temperature is not convertable to float", 400)

    if not (-273.15 <= temperature_float):
        return error_msg("Temperature bellow Absolute zero.", 400)

    device.temperature = temperature_float
    return save_and_return_device(device)


@app.route("/device/<device_id>/notes", methods=["POST"])
def set_notes(device_id: str):
    device = load_device(device_id)
    if device is None:
        return error_msg("Unknown ID", 400)

    device.notes = request.data.decode()
    return save_and_return_device(device)


if __name__ == "__main__":
    # print(type_to_class)
    app.run(debug=True)

