#!/usr/bin/env python3

def encode(s: str, n: int) -> str:
    str = [s[i:i + n] for i in range(0, len(s), n)]
    return "".join((s[::-1] for s in str))

def decode(s: str, n: int) -> str:
    str = [s[i:i + n] for i in range(0, len(s), n)]
    return "".join((s[::-1] for s in str))

def main():
    print(decode(encode("Dvered", 2), 2))

if __name__ == '__main__':
    main()
