#!/usr/bin/env python3

from turtle import Turtle

# Tuto funkci implementuj.
def spiral(turtle: Turtle, side_length: float, 
           angle: float, increment: float, max_length: float) -> None:
    turtle.forward(side_length)
    turtle.right(angle)
    if side_length+increment < max_length:
        spiral(turtle, side_length + increment, angle, increment, max_length)
    else:
        return

# Testy:
julie = Turtle()

#spiral(julie, 10, 90, 1, 9) # Prázdne
spiral(julie, .01, 89.5, 2, 367) # Vykreslí zadanú špirálu

