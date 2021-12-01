#! /usr/bin/env python3

import socket
from typing import Any, Tuple, Optional, List
import sys
import base64

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

    def __str__(self) -> str:
        return f"Error {{kind = {self.__kind}, data = {self.__data}, msg = {self.__msg}}}"


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

    def __str__(self) -> str:
        return f"ok = {self.ok}, err = {self.err}"


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
    def __init__(self, nick: str,
                 password: str,
                 ip: str=SERVER_IP,
                 port: int=PORT,
                 is_nsfw: bool=False,
                 meme: str="meme.png",
                 description: str="Default meme desc.") -> None:
        self.ip: str = ip
        self.port: int = port
        self.nick: str = nick
        self.password: str = password
        self.is_nsfw = is_nsfw
        self.meme_name = meme
        self.description: str = description

    def run(self) -> Result:
        main_channel = MainChannel(self.ip, self.port)
        # sum of all the data sent by the client
        sum = 0
        print("here")
        first_phase_result = main_channel.first_phase(self.nick)

        if first_phase_result.is_err():
            return first_phase_result

        token, data_port, data_size = first_phase_result.unwrap()
        sum += data_size

        data_channel = DataChannel(self.ip, data_port)
        second_phase_result = data_channel.second_phase(self.nick,
                                                        token,
                                                        self.meme_name,
                                                        self.description,
                                                        self.is_nsfw,
                                                        self.password)
        if second_phase_result.is_err():
            return second_phase_result
        
        dtoken, data_size = second_phase_result.unwrap()
        sum += data_size

        last_phase_result = main_channel.last_phase(dtoken, data_sum)
        
        if last_phase_result.is_err():
            return last_phase_result

        print("All three phases went, without an error!")
        print("Signing out...")

        return Result(ok=())


class Channel:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.connection: Optional[socket.socket]

    def connect(self) -> Result:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        self.connection = s
        return Result(ok=self.connection)

    @classmethod
    def encode_data(cls, data: str) -> Tuple[int, bytes]:
        data_lenght = len(data)
        data = f"{data_lenght}:{data},"
        return (data_lenght, b'{data}')

    @classmethod
    def decode_data(cls, data: bytes) -> Tuple[int, str]:
        decoded = data.decode("utf-8")
        index = decoded.find(":")
        data_length = len(decoded)
        decoded_data = decoded[index:]  # this should get rid of the trailing comma
        return (data_length, decoded_data)

    def send(self, data: str) -> Result:
        if self.connection:
            size, encoded_data = self.encode_data(data)
            self.connection.sendall(encoded_data)
            return Result(ok=size)
        else:
            return Result(err=Error("Send", msg="There is no connection."))

    def recieve(self, recieve_data_size: int) -> Result:
        buffer: List[str] = ["__init"]
        print(buffer)
        entire_package_size: int = 0
        if self.connection:
            while buffer[-1]:
                print(buffer)
                received_data = self.connection.recv(recieve_data_size)
                size, decoded = self.decode_data(received_data)  # not sure if we need the size here, but we probably do
                if decoded != "":
                    print(decoded)
                entire_package_size += size
                buffer.append(decoded)
            return Result(ok=buffer[1:])
        else:
            return Result(err=Error("Receive", "There is no connection."))


class MainChannel(Channel):
    """
    A class responsible for main channel communication.
    """
    def __init__(self, ip: str, port: int, ) -> None:
        super().__init__(ip, port)
        self.connection = self.connect().unwrap()

    def first_phase(self, nick: str, ) -> Result:
        data_to_send: List["str"] = ["C MTP V:1.0", f"C {nick}"]
        received_data: List["str"] = list()
        # sum of all the data sent by the client
        sum: int = 0
        
        send_result = self.send(data_to_send[0])

        if send_result.is_err():
            return send_result

        sum += send_result.unwrap()

        receive_result = self.recieve(1024)
        if receive_result.is_err():
            return receive_result

        received_data.append(receive_result.unwrap()[0])
        send_result = self.send(data_to_send[1])

        if send_result.is_err():
            return send_result

        sum += send_result.unwrap()

        receive_result = self.recieve(1024)
        if receive_result.is_err():
            return receive_result

        received_data.append(receive_result.unwrap()[0])

        receive_result = self.recieve(1024)
        if receive_result.is_err():
            return receive_result

        received_data.append(receive_result.unwrap()[0])

        return Result(ok=(received_data[1], received_data[2], sum))


class DataChannel(Channel):
    """
    A class responsible for handling the data channel and it's communication.
    """
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

    def second_phase(self, nick: str,
                     token: str,
                     meme_name: str,
                     description: str,
                     is_nsfw: bool,
                     password: str) -> Result:
        meme_img = ""
        with open(meme_name, "rb") as f:
            meme_img = base64.b64encode(f.read())

        data_to_send = {
                "nick": f"C {nick}",
                "meme": f"C {meme_img}",
                "description": f"C {description}",
                "nsfw": f"C {str(is_nsfw).lower()}",
                "password": f"C {password}"
                }
        received_data: List[str] = list()
        sum: int = 0

        initial_contact_result = self.send(data_to_send["nick"])
        if initial_contact_result.is_err():
            return initial_contact_result
        sum += initial_contact_result.unwrap()

        receive_result = self.recieve(1024)
        first = True
        last_data_length = 0
        dtoken = None

        while receive_result:
            if receive_result.is_err():
                return receive_result
            else:
                if receive_result.unwrap() and first:
                    _, data = receive_result.unwrap()
                    if data:
                        if data[1] != token:
                            # TODO: self.send_error("tokens dont match!")
                            pass
                        received_data.append(data[1])
                        first = False
                if data := receive_result.unwrap()[1] == "S REQ:meme":
                    res = self.send(data_to_send["meme"])
                    if res.is_err():
                        return res
                    res = res.unwrap()
                    sum += res
                    last_data_length = res
                if data := receive_result.unwrap()[1] == "S REQ:description":
                    res = self.send(data_to_send["description"])
                    if res.is_err():
                        return res
                    res = res.unwrap()
                    sum += res
                    last_data_length = res[0]
                if data := receive_result.unwrap()[1] == "S REQ:nsfw":
                    res = self.send(data_to_send["nsfw"])
                    if res.is_err():
                        return res
                    res = res.unwrap()
                    sum += res
                    last_data_length = res[0]
                if data := receive_result.unwrap()[1] == "S REQ:password":
                    res = self.send(data_to_send["password"]).is_err()
                    if res.is_err():
                        return res
                    res = res.unwrap()
                    sum += res
                    last_data_length = res[0]
                if "S ACK:" in receive_result.unwrap()[1]:
                    stripped = receive_result.unwrap()[1].removeprefix("S ACK:")
                    if int(stripped) != last_data_length:
                        return Result(err=Error("DataChannel",
                                                msg="Data lenght not same."))
                if "S END:" in receive_result.unwrap()[1]:
                    stripped = receive_result.unwrap()[1].removeprefix("S END:")
                    dtoken = stripped
                    break
        print("All went well!")
        return Result(ok=dtoken)


def main() -> None:
    mtp = MTP("jozko", "dvere", meme="dvere.jpg")
    result = mtp.run()
    if result.is_ok():
        print("Done!")
    else:
        print(str(result))


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
