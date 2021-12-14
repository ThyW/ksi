#!/usr/bin/env python3

from flask import Flask, render_template
import requests
import json

#  import all the necessary data classes.
#  Roomate, Device, more to come


app = Flask(__name__, template_folder="templates")


@app.route('/')
def index() -> str:
    return render_template('home.html')


@app.route('/overview')
def overview() -> str:
    return render_template('overview.html')

def main() -> None:
    app.debug = True
    app.run()


if __name__ == "__main__":
    main()
