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
        l = list()
        count = 0
        data = soc.recv(1024)
        buffer = list()
        while data:
            parsed = data.decode().rstrip().strip()
            buffer.append(parsed)
            parsed = parsed.strip()
            if parsed == "*":
                count += 1
            if parsed != "*":
                if not len(parsed) > 20:
                    parsed = parsed.replace("\x1b[1D*", "").replace("\x1b[", "").strip()
                    l.append(parsed)
            data = soc.recv(1024)
        final = list()

        for ii, each in enumerate(l):
            if each.startswith("*"):
                a = each.replace("*", "")
                final.append(a)
            elif len(each) == 1 and (not l[ii - 1][-1].islower() or l[ii - 1][-1] == "_"):
                final.append(l[ii - 1] + each)
                del final[len(final) - 2]
            else:
                final.append(each)

        ll = ["*" for _ in range(len(final) + 1)]
        debug = []
        
        cursor = len(final) - 2
        for part in final:
            t = (part[0:len(part) - 1], part[len(part) - 1])
            if t[0] == None:
                debug.append(cursor + 1)
                ll[cursor + 1] = t[1]
            elif "D" in t[0]:
                a = t[0].replace("D", "")
                cursor -= int(a) - 1
                debug.append(cursor)
                ll[cursor] = t[1]
            elif "C" in t[0]:
                a = t[0].replace("C", "")
                cursor += int(a) + 1
                debug.append(cursor)
                ll[cursor] = t[1]
        print("KSI{" + "".join(ll).removesuffix("*"))
main3()
