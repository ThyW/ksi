#! /usr/bin/env python3

import socket

SERVER_IP = "159.89.4.84"
PORT = 42069


class MTP:
    """
    A class reponsible for MTP communication
    :param ip - IP Address of the server we want to communicate with
    """
    def __init__(self, ip: str=SERVER_IP, port: int=PORT) -> None:
        self.ip = ip
        self.port = port


class Channel:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port


class MainChannel(Channel):
    """
    A class responsible for main channel communication.
    """
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)


class DataChannel(Channel):
    """
    A class responsible for handling the data channel and it's communication.
    """
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)
