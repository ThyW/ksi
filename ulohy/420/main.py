#!/usr/bin/env python3
from turtle import Turtle

julie = Turtle()

# Tuto funkci implementuj.
def draw_tree(turtle: Turtle, length: int, min_length: int) -> None:
    """
	Parametry:
	julie: instancia triedy Turtle.
	length: dĺžka vetvy v každom individuálnom rekurzívnom volaní.
	min_length: udáva dĺžku najkratšej možnej vetvy
	"""
    if length <= min_length:
        return

    turtle.forward(length)
    turtle.left(30)
    draw_tree(turtle, int(round(length * (2 / 3), 2)), min_length)
    turtle.right(60)
    draw_tree(turtle, int(round(length * (2 / 3), 2)), min_length)
    turtle.left(30)
    turtle.backward(length)# Upravuj iba kód NAD týmto komentárom
    
julie.penup()
julie.goto(0, -120)
julie.pendown()
julie.lt(90)

# Testy:
# Strom z obrázku
#draw_tree(julie, 120, 20)

# Strom, na ktorom sa testuje
draw_tree(julie, 120, 5) # NEZABUDNI PRED ODOVZDANÍM ODKOMENTOVAŤ!

