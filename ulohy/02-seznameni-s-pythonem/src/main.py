#!/usr/bin/env python3

inp = int(input()) 
if not (inp >= 2 and inp < 500):
    exit()
pow = 0
h = 1

while pow < 500:
    pow = inp ** h
    h += 1

if pow > 500:
    print(inp ** (h - 2))
