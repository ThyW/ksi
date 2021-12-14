import time

from flask import url_for
from typing import List, Tuple, Optional, Union
from time import sleep
import json
import urllib.parse
import requests
import pytest
from pprint import pprint

from devices_offline import *
import device_simulator


@pytest.fixture
def app():
    app = device_simulator.app
    return app


def test_new_device_creation(client):
    assert client.get(url_for("new_smart_light", _external=True)).status_code == 200
    assert client.get(url_for("new_smart_plug", _external=True)).status_code == 200
    assert client.get(url_for("new_smart_radiator", _external=True)).status_code == 200
    assert client.get(url_for("new_temperature_sensor", _external=True)).status_code == 200
    assert client.get(url_for("new_motion_sensor", _external=True)).status_code == 200
    assert client.get(url_for("new_switch_sensor", _external=True)).status_code == 200


def test_smart_light(client):
    resp1 = client.get(url_for("new_smart_light", _external=True))
    assert resp1.status_code == 200

    device = resp1.json
    pprint(device)
    assert device["power_usage"] == 0

    assert client.get(device["actions"]["change_color_blue_sky"]).status_code == 200
    assert client.get(device["actions"]["turn_on"]).status_code == 200
    time.sleep(1)

    resp2 = client.get(device["actions"]["turn_off"])
    pprint(resp2.json)
    assert resp2.status_code == 200
    assert 0 < resp2.json["power_usage"] < 1000


def test_motion_sensor(client):
    resp1 = client.get(url_for("new_motion_sensor", _external=True))
    assert resp1.status_code == 200

    device = resp1.json
    pprint(device)

    resp2 = client.get(device["actions"]["trigger_report"])  # this might not success, the client is not recursive
    print(resp2)


def test_light_temperature(client):
    resp1 = client.get(url_for("new_smart_light", _external=True))
    assert resp1.status_code == 200
    pprint(resp1.json)

    resp2 = client.get(resp1.json["actions"]["change_color_blue_sky"])
    assert resp2.status_code == 200
    assert resp2.json["color_temperature"] == 10000
    print(resp2)


def test_change_collector_url(client):
    resp1 = client.get(url_for("new_motion_sensor", _external=True))
    assert resp1.status_code == 200
    pprint(resp1.json)

    new_collector_url = 'https://example.com'
    url_set = f'{url_for("change_report_url", device_id=resp1.json["id"], _external=True)}?url={urllib.parse.quote_plus(new_collector_url)}'

    resp2 = client.get(url_set)
    print(resp2)
    assert resp2.status_code == 200
    assert urllib.parse.unquote_plus(resp2.json["collector_url"]) == new_collector_url
