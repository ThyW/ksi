#!/usr/bin/env python3

from turtle import Turtle, done

def a():
    j = Turtle()
    size = 100
    angle = 360 / 5

    for i in range(5):
        j.forward(size)
        j.left(angle)
    done()

def b():
    j = Turtle()
    size = 100
    for i in range(3, 9):
        for l in range(i):
            angle = 360 / i
            j.forward(100)
            j.left(angle)
    done()
b()
