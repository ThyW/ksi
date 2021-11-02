#!/usr/bin/env python3

import flask

app = flask.Flask("Flask app")


@app.route("/")
def index() -> str:
    return "<p>Hello world</p>"
