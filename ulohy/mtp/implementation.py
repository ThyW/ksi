#! /usr/bin/env python3

import socket
from typing import Any, Tuple, Optional, Union
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

    def unwrap(self) -> Any:
        if self.is_ok():
            return self.ok

    def error(self) -> Optional[Error]:
        if self.is_err():
            return self.err
        else:
            return


class ChannelError(Error):
    """
    All the errors that can happen when working with channels.
    """
    def __init__(self, kind: Any = None, data: Any = None ,msg: str = None) -> None:
        super().__init__(kind, data=data, msg=msg)


class ChannelResult(Result):
    def __init__(self, ok: Any = None, err: ChannelError = None) -> None:
        super().__init__(ok=ok, err=err)


class MTPError(Error):
    def __init__(self, kind: Any, kind_data: Any = None) -> None:
        super().__init__(kind, kind_data)

class MTPResult(Result):
    """
    Representation of either succes or failure when working with MTP.
    """
    def __init__(self, ok: Any = None, err: Error = None) -> None:
        super().__init__(ok=ok, err=err)


class MTP:
    """
    A class reponsible for MTP communication
    :param ip - IP Address of the server we want to communicate with
    """
    def __init__(self, nick: str, password: str, ip: str=SERVER_IP, port: int=PORT,  is_nsfw: bool = False, meme: str = None) -> None:
        self.ip: str = ip
        self.port: int = port
        self.nick: str = nick
        self.password: str = password
        self.is_nsfw = is_nsfw

    def run(self) -> MTPResult:
        return MTPResult(ok=())


class Channel:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.connection: Optional[socket.socket]

    def connect(self) -> ChannelResult:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if con := s.connect((self.ip, self.port)):
            self.connection = con
            return ChannelResult(ok=())
        else:
            return ChannelResult(err=ChannelError("Connect"))

    @classmethod
    def encode_data(cls, data: str) -> Tuple[int, bytes]:
        data_lenght = len(data)
        data = f"{data_lenght}:{data}"
        return (data_lenght, b'{data}')

    @classmethod
    def decode_data(cls, data: bytes) -> Tuple[int, str]:
        decoded = data.decode("utf-8")
        return (len(decoded), decoded)

    def send(self, data: str) -> ChannelResult:
        if self.connection:
            size, encoded_data = self.encode_data(data)
            self.connection.sendall(encoded_data)
            return ChannelResult(ok=size)
        else:
            return ChannelResult(err=ChannelError("Send"))

    def recieve(self, amount: int) -> ChannelResult:
        if self.connection:
            buffer = self.connection.recv(amount)
            size, decoded = self.decode_data(buffer)
            return ChannelResult(ok=(size, decoded))
        else:
            return ChannelResult(err=ChannelError("Receive"))


class MainChannel(Channel):
    """
    A class responsible for main channel communication.
    """
    def __init__(self, ip: str, port: int, ) -> None:
        super().__init__(ip, port)


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
    print(ChannelResult(ok=()).unwrap())
    print(MTPResult(ok=()).unwrap())
    print(MTPResult(err=MTPError("Channel", "Send")).unwrap().kind())


def run_module_tests() -> None:
    test_result()


if "--test" in sys.argv:
    run_module_tests()
