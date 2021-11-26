#! /usr/bin/env python3

import socket
from typing import Any, Tuple, Optional, List
import sys

SERVER_IP = "159.89.4.84"
PORT = 42069


class Error:
    """
    Base class for all errors, which allows additional context to be passed with your error.
    """
    def __init__(self, kind: Any = None, data: Any = None, msg: str = None) -> None:
        self.__kind = kind
        self.__data = data
        self.__msg = msg

    def message(self) -> Optional[str]:
        return self.__msg

    def kind(self) -> Optional[Any]:
        if self.__kind:
            if self.__data:
                return (self.__kind, self.__data)
            return self.__kind
        else:
            return None


# Why not become a little rust-y? ;)
# https://doc.rust-lang.org/std/result/enum.Result.html
class Result:
    """
    Representation of either success or failure.
    """
    def __init__(self, ok: Any = None, err: Error = None) -> None:
        self.ok = ok
        self.err = err

    def is_ok(self) -> bool:
        return self.ok is not None

    def is_err(self) -> bool:
        return self.err is not None

    def unwrap(self) -> Optional[Any]:
        if self.is_ok():
            return self.ok

    def error(self) -> Optional[Error]:
        if self.is_err():
            return self.err


class MTP:
    """
    A class reponsible for MTP communication
    :param nick - User's nick.
    :param password - User's password.
    :param ip - IP Address of the server we want to communicate with.
    :param port - Port on which we want to communicate.
    :param meme - filename pointing to the image which we want to send.
    :param is_nsfw - Whether the meme should be marked as nsfw.
    """
    def __init__(self, nick: str, password: str, ip: str=SERVER_IP, port: int=PORT,  is_nsfw: bool = False, meme: str = None) -> None:
        self.ip: str = ip
        self.port: int = port
        self.nick: str = nick
        self.password: str = password
        self.is_nsfw = is_nsfw
        self.meme_name = meme

    def run(self) -> Result:
        return Result(ok=())


class Channel:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.connection: Optional[socket.socket]

    def connect(self) -> Result:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if con := s.connect((self.ip, self.port)):
            self.connection = con
            return Result(ok=())
        else:
            return Result(err=Error("Connect"))

    @classmethod
    def encode_data(cls, data: str) -> Tuple[int, bytes]:
        data_lenght = len(data)
        data = f"{data_lenght}:{data},"
        return (data_lenght, b'{data}')

    @classmethod
    def decode_data(cls, data: bytes) -> Tuple[int, str]:
        decoded = data.decode("utf-8")
        index = decoded.find(":")
        data_length = int(decoded[0:index]) or len(decoded)
        decoded_data = decoded[index:]  # this should get rid of the trailing comma
        return (data_length, decoded_data)

    def send(self, data: str) -> Result:
        if self.connection:
            size, encoded_data = self.encode_data(data)
            self.connection.sendall(encoded_data)
            return Result(ok=size)
        else:
            return Result(err=Error("Send"))

    def recieve(self, recieve_data_size: int) -> Result:
        buffer: List[str] = ["__init"]
        entire_package_size: int = 0
        if self.connection:
            while buffer[-1][-1] != ",":
                received_data = self.connection.recv(recieve_data_size)
                size, decoded = self.decode_data(received_data)  # not sure if we need the size here, but we probably do
                entire_package_size += size
                buffer.append(decoded)
            return Result(ok=buffer[1:])
        else:
            return Result(err=Error("Receive"))


class MainChannel(Channel):
    """
    A class responsible for main channel communication.
    """
    def __init__(self, ip: str, port: int, ) -> None:
        super().__init__(ip, port)

    def first_phase(self, nick: str, ) -> Result:
        data_to_send: List["str"] = ["C MTP V:1.0", f"C {nick}"]
        received_data: List["str"] = list()
        
        send_result = self.send(data_to_send[0])

        if send_result.is_err():
            return send_result

        receive_result = self.recieve(1024)
        if receive_result.is_err():
            return receive_result

        received_data.append(receive_result.unwrap()[1])
        send_result = self.send(data_to_send[1])

        if send_result.is_err():
            return send_result

        receive_result = self.recieve(1024)
        if receive_result.is_err():
            return receive_result

        received_data.append(receive_result.unwrap()[1])

        receive_result = self.recieve(1024)
        if receive_result.is_err():
            return receive_result

        received_data.append(receive_result.unwrap()[1])

        return Result(ok=(received_data[1], received_data[2]))



class DataChannel(Channel):
    """
    A class responsible for handling the data channel and it's communication.
    """
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)


def main() -> None:
    mtp = MTP("jozko", "dvere")
    result = mtp.run()
    if result.is_ok():
        print("Done!")
    else:
        print(result.unwrap().kind())


if __name__ == "main":
    main()


def test_result() -> None:
    print(Result(ok=()).unwrap())
    print(Result(err=Error(kind="Test", data="some data", msg="Error description.")).unwrap())
    print(Result(err=Error("Channel", "Send")).error().kind())


def own_test() -> None:
    some = ["aaa", "bbbbb", "cccc,", "hihihi"]
    buffer = ["start"]
    while buffer[-1][-1] != ",":
        buffer.append(some.pop(0))
    assert buffer[1:] == ["aaa", "bbbbb", "cccc,"]

    print("passed")


def run_module_tests() -> None:
    test_result()


if "--test" in sys.argv:
    run_module_tests()
    own_test()
