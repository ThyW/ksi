#! /usr/bin/env python3

import pynetstring
import socket
import base64
from socket import socket as Socket

from typing import Tuple, NamedTuple, Union, List


SERVER_IP = "159.89.4.84"
PORT = 42069


class Meme(NamedTuple):
    nick: str
    password: str
    description: str
    meme_file: str
    is_nsfw: bool = False


class Mtp:
    def __init__(self, ip: str, port: int, meme: "Meme") -> None:
        self.meme = meme
        self.ip = ip
        self.port = port
        self.status: str = "Not run yet!"

    def __str__(self) -> str:
        return f"ip: {self.ip}, port: {self.port}, meme: {self.meme}"

    def run(self) -> None:
        self.status = "Started running!"
        size: int = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            fsize, token, data_port = self.first_phase(s)
            size += fsize
            dt = ""
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ds:
                ds.connect((self.ip, int(data_port)))
                fsize, dtoken = self.second_phase(ds, token)
                if fsize == 0 and dtoken == "":
                    return
                size += fsize
                dt = dtoken
            self.final_phase(s, dt, size)

    def first_phase(self, sock: Socket) -> Tuple[int, str, str]:
        total_data_sent_size: int = 0
        data_send = ["C MTP V:1.0", f"C {self.meme.nick}"]
        data_receive = []

        sock.sendall(pynetstring.encode(data_send[0]))
        total_data_sent_size += len([data_send[0]])

        data = self.recieve(sock)
        data_receive.append(data[1])

        sock.sendall(pynetstring.encode(data_send[1]))
        total_data_sent_size += len([data_send[1]])

        data = self.recieve(sock)
        data_receive.append(data[1])

        data = self.recieve(sock)
        data_receive.append(data[1])

        return (total_data_sent_size, data_receive[1], data_receive[2])

    def second_phase(self, sock: Socket, token: str) -> Tuple[int, str]:
        total_data_sent_size: int = 0
        data_send = {
                "nick": f"C {self.meme.nick}",
                "meme": f"C {self.send_file()}",
                "isNSFW": f"C {self.is_nsfw_f()}",
                "description": f"C {self.meme.description}",
                "password": f"C {self.meme.password}",
                }
        data_receive = []

        sock.sendall(pynetstring.encode(data_send["nick"]))
        total_data_sent_size += len([data_send["nick"]])

        data = self.recieve(sock)
        data_receive.append(data)
        rc_token = data[1]

        if rc_token != token:
            sock.sendall(pynetstring.encode("E Tokens are not the same!"))
            self.status = "Error: Token mismatch!"
            return (0, "")

        _, data = self.recieve(sock)

        last_data_length = 0
        while data:
            if "END:" in data:
                return (total_data_sent_size, data.removeprefix("END:"))
            if "ACK:" in data:
                if int(data.removeprefix("ACK:")) != last_data_length:
                    sock.sendall(pynetstring.encode("E dataLength mismatch!"))
                    self.status = f"Error: size mismatch on {data}, {last_data_length}"
                    return (0, "")
            if "REQ:" in data:
                type = data.removeprefix("REQ:")
                what = data_send[type]
                last_data_length = len(what) - 2
                enc = pynetstring.encode(what)
                sock.sendall(enc)
                # print(f"{type}: {enc}")
                total_data_sent_size += last_data_length
            _, data = self.recieve(sock)

    def final_phase(self, sock: Socket, dtoken: str, size: int) -> None:
        _, data = self.recieve(sock)
        if int(data) != size - 3:
            print("size mismatch")
            self.status = f"Error: size mismatch: {int(data)} != {size - 3}"
            sock.sendall(pynetstring.encode("E size mismatch"))
            return

        sock.sendall(pynetstring.encode(f"C {dtoken}"))

        _, data = self.recieve(sock)
        if data == "ACK":
            self.status = "[SUCCES] Transaction was successful!"

    def stripper(self, expr: bytes) -> List[str]:
        return expr.decode("utf-8").removeprefix('S ')

    def recieve(self, sock: Socket) -> Tuple[int, str]:
        decoder = pynetstring.Decoder()
        data = sock.recv(8128)
        data = [item for item in decoder.feed(data)]

        return (len(data[0]), self.stripper(data[0]))

    def is_nsfw_f(self) -> str:
        if self.meme.is_nsfw:
            return "true"
        else:
            return "false"

    def send_file(self) -> str:
        # print(self.meme.meme_file)
        with open(self.meme.meme_file, "rb") as memimage:
            s = base64.b64encode(memimage.read())
        return s.decode("utf-8")

    def get_status(self) -> str:
        return self.status


def test() -> None:
    mtp = Mtp(SERVER_IP, PORT, Meme("dvere", "erevd", "dvere", "./dvere.jpeg"))
    mtp.run()
