#!/usr/bin/env python3

import array
import socket
import sys

def main1() -> None:
    ip, port = sys.argv[1], sys.argv[2] 

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((ip, port))
        soc.sendall(b"HELLO")
        buff = array.array("i")
        data = soc.recv(1024)
        print(data.decode().rstrip())


def main2() -> None:
    hostname, port = sys.argv[1], int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((hostname, port))
        data = soc.recv(1024)
        while data:
            parsed = data.decode().rstrip()
            if parsed.startswith("KSI"):
                print(parsed)
                return
            parsed = parsed.removeprefix("Kolik je ")
            parsed = parsed.removesuffix(", plantazniku?")
            list = parsed.split("+")
            s = str.encode(f"{int(list[0]) + int(list[1])}")
            soc.sendall(s)
            data = soc.recv(1024)


def main3() -> None:
    hostname, port = sys.argv[1], int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((hostname, port))
        cursor = 0
        buffer = list()
        count = 0
        data = soc.recv(1024)
        while data:
            parsed = data.replace(b"\x1b[1D*", b"")
            parsed = parsed.replace(b"\x1b[", b"")
            parsed = parsed.replace(b"*", b"")
            if not len(parsed) > 5 and not len(parsed) == 0:
                # print(f"{parsed}: {len(parsed)}")
                count += 1
                buffer.append(parsed)
            data = soc.recv(1024)

        output = ["*"] * len(buffer)
        cursor = len(output) - 1
        for each in buffer:
            f = str(each)
            l = len(each) 
            i = 0
            num = None
            method = 0
            char = ""
            while i < l:
                if f[i].isdigit():
                    if not num:
                        num = f[i]
                    else:
                        num += f[i] 
                
                if f[i] == b"D":
                    method = -1
                if f[i] == b"C":
                    method = 1
                else:
                    char = chr(each[i])
                i += 1
            if num:
                cursor += ((int(num) * method))
            else:
                cursor += 1
            print(f"{f} {num} {method} {char}")
            print(cursor)
            output[cursor] = char
            cursor += 1
        print(output)

main3()
