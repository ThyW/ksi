#!/usr/bin/env python3

import turtle
import random
from typing import Deque, Tuple
from turtle import Vec2D
import re
"""
S - starting nonterminal
f - forward terminal
b - backward terminal
rXXX - right turn by XXX angle where  0 <= XXX <= 180 (terminal)
lXXX - left turn by XXX angle where  0 <= XXX <= 180 (terminal)
[ push position terminal
] pop position terminal
{A .. Z, +, - .. } / S nonterminal building symbols
"""


class L_system:
    angle = 60  # 0 <= angle <= 180

    """
    First starting rule S ->  ..
    Basic rules in form A -> B+A ...  combination of angles and nonterminals
    Terminal rules aplied after last iteration A -> f / b / rXXX / lXXX
    """
    expansion_rules = {}  # dict, left side key, right side rewritten rule
    terminal_rules = {}

    def __init__(self, distance: int,
                 angle: float,
                 expansion_rules: dict[str, str],
                 terminal_rules: dict[str, str]):
        self.distance: int = distance
        self.angle: float = angle
        self.expansion_rules: dict[str, str] = expansion_rules
        self.terminal_rules: dict[str, str] = terminal_rules
        # get str angle
        strAngle = str(self.angle)
        if self.angle < 10:
            strAngle = "00" + strAngle
        elif self.angle < 100:
            strAngle = "0" + strAngle
        self.strAngle: str = strAngle

    # helper so that I dont have to copy it into every test
    def add_basic_angles(self):
        self.terminal_rules['+'] = "r" + self.strAngle
        self.terminal_rules['-'] = "l" + self.strAngle


class L_builder:
    axiom = "S"

    def __init__(self, system: "L_system"):
        self.__system: "L_system" = system

    # do not change the head of the function
    def build_system(self, iterations: int):
        self.axiom: str = L_builder.axiom
        for _ in range(iterations - 1):
            # make an intermediate axiom representation
            temp_axiom: str = self.axiom
            # check for the final iteration
            # for char in self.axiom:
            #     for (key, value) in self.__system.expansion_rules.items():
            #         if char == key:
            #             temp_axiom += value
            # self.axiom = temp_axiom
            # print(self.axiom)

            for key, value in self.__system.expansion_rules.items():
                if type(value) == "list":
                    value = random.choice(value)
                temp_axiom = temp_axiom.replace(key, value)
            self.axiom = temp_axiom
            print(self.axiom)

        temp_axiom: str = self.axiom
        for (key, value) in self.__system.terminal_rules.items():
                # check each char against the terminal rules and build 
                # a new axiom out of that
            temp_axiom = temp_axiom.replace(key, value)
        self.axiom = temp_axiom
        
    def get_axiom(self):
        return self.axiom
    

class L_drawer:
    # change speed for your animation but submit with speed 0
    speed = 0

    def __init__(self, axiom, distance, startPos, startAngle):
        self.__axiom = axiom
        self.__distance = distance  # distance for turtle forward / backward
        self.startPos = startPos  # initial position of turtle
        self.startAngle = startAngle  # initial angle

    # do not change the head of the function
    def draw_L_system(self):
        wn = turtle.Screen()
        pen = turtle.Turtle()

        turtle.setpos(self.startPos)
        turtle.setheading(self.startAngle)

        turtle.tracer(0, 0)  # stop the drawing animation

        for i, char in enumerate(self.__axiom):
            if char == "f":
                turtle.forward(self.__distance)
            elif char == "b":
                turtle.backward(self.__distance)
            elif char == "[":
                self.stack_push((turtle.position(), turtle.heading()))
            elif char == "]":
                pos = self.stack_pop()
                turtle.setpos(pos[0])
                turtle.setheading(pos[1])
            elif char == "r":
                angle = self.__axiom[i + 1: i + 4]
                angle = [int(char) for char in angle]
                angle = angle[0] * 100 + angle[1] * 10 + angle[2] * 1
                turtle.right(angle) 
            elif char == "l":
                angle = self.__axiom[i + 1: i + 4]
                angle = [int(char) for char in angle]
                angle = angle[0] * 100 + angle[1] * 10 + angle[2] * 1
                turtle.left(angle) 
            else:
                continue

        turtle.update()  # show the drawing
        # uncomment if you want to see the drawing
        # keep commented in submision file
        # wn.mainloop()
        pen.clear()  # clear previous drawing from canvas [for automated tests]

    def init_stack(self):
        from collections import deque
        # create a Deque class for simple pushing and popping from the front
        self.stack = deque([])

    def stack_push(self, pos: Tuple[Vec2D, float]):
        self.stack.appendleft(pos)

    def stack_pop(self) -> Tuple[Vec2D, float]:
        return self.stack.popleft()

def test_line(depth):
    expansion_rules = {
                    "S": "F",
                    "F": "FF"
                    }

    terminal_rules = {
                    "F": "f"
                    }

    system = L_system(10, 0, expansion_rules, terminal_rules)

    builder = L_builder(system)
    builder.build_system(depth)
    axiom = builder.get_axiom()

    drawer = L_drawer(axiom, system.distance, (-250, -200), 45)
    # enable drawing for testing, but submit without it !!!!
    # drawer.draw_L_system()

    return axiom


def test_koch(depth):
    expansion_rules = {
                    "S": "F",
                    "F": "F-F++F-F"
                    }

    terminal_rules = {
                    "F": "f",
                    "S": "f",
                    "+": "r045",
                    "-": "l045"
                    }
    system = L_system(10, 45, expansion_rules, terminal_rules)

    system.add_basic_angles()

    builder = L_builder(system)
    builder.build_system(depth)
    axiom = builder.get_axiom()

    drawer = L_drawer(axiom, system.distance, (-250, -200), 0)
    # enable drawing for testing, but submit without it !!!!
    # drawer.draw_L_system()

    return axiom


def test_sierpinsky_triangle(depth):

    expansion_rules = {
                    "S": "F-G-G",
                    "F": "F-G+F+G-F",
                    "G": "GG"
                    }

    terminal_rules = {
                    "F": "f",
                    "S": "f",
                    "G": "f"
                    }
    system = L_system(20, 120, expansion_rules, terminal_rules)

    system.add_basic_angles()

    builder = L_builder(system)
    builder.build_system(depth)
    axiom = builder.get_axiom()

    drawer = L_drawer(axiom, system.distance, (-300, -340), 0)
    # enable drawing for testing, but submit without it !!!!
    # drawer.draw_L_system()

    return axiom


def test_barley_deterministic(depth):

    expansion_rules = {
                    "S": "X",
                    "X": "F-[[X]+X]+F[+FX]-X",
                    "F": "FF"
                    }

    terminal_rules = {
                    "F": "f",
                    "S": "f",
                    "X": "",
                    "[": "[",
                    "]": "]"
                    }

    system = L_system(8, 25, expansion_rules, terminal_rules)

    system.add_basic_angles()

    builder = L_builder(system)
    builder.build_system(depth)
    axiom = builder.get_axiom()

    drawer = L_drawer(axiom, system.distance, (-300, 300), 45)
    # enable drawing for testing, but submit without it !!!!
    # drawer.draw_L_system()

    return axiom


# use function random.choice() to choose nonterminals from list
def test_barley_non_deterministic(depth, seed):
    random.seed(seed)
    expansion_rules = {
                    "S": "[X]T[X]TX",
                    "X": ["F-[[X]+X]+F[+FX]-X", "F+[[X]-X]-F[-FX]+X"],
                    "F": 5*["FF"] + ["F"],
                    "T": "uMFFLd"
                    }

    terminal_rules = {
                    "F": "f",
                    "S": "f",
                    "X": "",
                    "[": "[",
                    "]": "]",
                    "M": "r090",
                    "L": "l090",
                    }
    system = L_system(4, 17.5, expansion_rules, terminal_rules)
    system.add_basic_angles()

    builder = L_builder(system)
    builder.build_system(depth)
    axiom = builder.get_axiom()

    drawer = L_drawer(axiom, system.distance, (-300, -340), 90)
    # enable drawing for testing, but submit without it !!!!
    # drawer.draw_L_system()

    return axiom


def test_harder_recursive(depth):  # "Dragon" barley

    expansion_rules = {
                    "S": "X",
                    "X": "F-[[X]+X]+F[+FX]-X[H]",
                    "F": "FF",
                    "H": "HLG",
                    "G": "HRG"
                    }

    terminal_rules = {
                    "F": "fff",
                    "G": "ff",
                    "H": "ff",
                    "S": "f",
                    "X": "",
                    "[": "[",
                    "]": "]",
                    "L": "l090",
                    "R": "r090"
                    }

    system = L_system(2, 25, expansion_rules, terminal_rules)

    system.add_basic_angles()

    builder = L_builder(system)
    builder.build_system(depth)
    axiom = builder.get_axiom()

    drawer = L_drawer(axiom, system.distance, (-300, -300), 45)
    # enable drawing for testing, but submit without it !!!!
    drawer.draw_L_system()

    return axiom

# ========================================
# Part with recursive functions
# ========================================


# very basic prolonging line
# example recursive function with same functionality as test_line(depth)
def line_recursive(depth):
    if depth <= 1:
        return "f"
    s = line_recursive(depth - 1)
    s += line_recursive(depth - 1)
    return s

# !! Test drawing lines with this function but in the code bellow
# create lines using "f" * {formula} // formula for line length !!


# TODO, recursive function that creates Koch Curve
def koch_curve_recursive(depth):
    pass


# TODO, recursive function that creates Sierpinsky triangle
def sierpinsky_triangle_recursive(depth):
    pass


# TODO, recursive function that creates "Dragon" Barley
# similar to test_harder_recursive grammar
def harder_recursive(depth):
    pass

# ========================================
# Part with grammar creation
# ========================================


def forward_right(depth):
    if depth <= 0:
        return "f"
    s = (depth - 1) * "f" + "r010"
    s += forward_right(depth - 1)
    return s


def forward_left(depth):
    if depth <= 0:
        return "f"
    s = (depth - 1) * "f" + "l010"
    s += forward_left(depth - 1)
    return s


def branch(depth):
    if depth <= 0:
        return "f"
    s = (depth - 1) * "b" + "[l090"
    s += forward_left(depth - 1)
    s += "][r090"
    s += forward_right(depth - 1)
    s += "]"
    s += branch(depth - 1)
    return s


def branch_root(depth):
    if depth <= 0:
        return ""
    s = "[l090"
    s += forward_left(depth - 1)
    s += "][r090"
    s += forward_right(depth - 1)
    s += "]"
    s += branch(depth - 1)
    return s


def circle(depth):
    if depth <= 0:
        return ""
    branchString = branch_root(depth - 1)
    s = "[" + 3 * (depth - 1) * "f" + branchString + "]"
    helper = "r090" + "[" + 3 * (depth - 1) * "f" + branchString + "]"
    s += helper * 3
    return s


def distorted_plane(depth):
    if depth <= 0:
        return ""
    branchString = branch_root(depth - 1)
    s = "[" + branchString + "]"
    helper = "r090" + "[" + branchString + "]"
    s += helper * 3
    return s


def chaos(depth):
    s = circle(depth - 1)
    s += distorted_plane(depth - 1)
    return s


# TODO function, add rules so it does exactly what above chaos function does
def test_chaos(depth):

    expansion_rules = {
                    # TODO
                    }

    terminal_rules = {
                    # TODO
                    }

    system = L_system(10, 0, expansion_rules, terminal_rules)

    builder = L_builder(system)
    builder.build_system(depth)
    axiom = builder.get_axiom()

    drawer = L_drawer(axiom, system.distance, (0, 0), 90)
    # drawer.draw_L_system()
    return axiom, expansion_rules, terminal_rules


# implementation of bonus function that builds recursive functions
def Bonus(Lsystem):
    pass


# Basic tests
# Don't forget to test edge cases
def basic_tests():
    # L system tasks
    assert test_line(6) == """ffffffffffffffffffffffffffffffff"""

    assert test_koch(3) == """fl045fr045r045fl045fl045fl045fr045r045fl045fr045r045fl045fr045r045fl045fl045fl045fr045r045fl045f"""

    assert test_sierpinsky_triangle(3) == """fl120fr120fr120fl120fl120ffr120fl120fr120fr120fl120fr120ffl120fl120fr120fr120fl120fl120ffffl120ffff"""

    assert test_barley_deterministic(3) == """ffl025[[fl025[[]r025]r025f[r025f]
    l025]r025fl025[[]r025]r025f[r025f]l025]r025ff[r025fffl025[[]r025]r025f[r025
    f]l025]l025fl025[[]r025]r025f[r025f]l025"""

    assert test_barley_non_deterministic(2, 5) == """[fr017.5[[]l017.5]l017.5f[
    l017.5f]r017.5]ur090ffl090d[fr017.5[[]l017.5]l017.5f[l017.5f]r017.5]ur090ff
    l090dfl017.5[[]r017.5]r017.5f[r017.5f]l017.5"""

    assert test_barley_non_deterministic(2, 190) == """[fl017.5[[]r017.5]r017.5
    f[r017.5f]l017.5]ur090ffl090d[fl017.5[[]r017.5]r017.5f[r017.5f]l017.5]ur090
    ffl090dfr017.5[[]l017.5]l017.5f[l017.5f]r017.5"""

    assert test_harder_recursive(3) == """ffffffl025[[fffl025[[]r025]r025fff[r0
    25fff]l025[ff]]r025fffl025[[]r025]r025fff[r025fff]l025[ff]]r025ffffff[r025f
    ffffffffl025[[]r025]r025fff[r025fff]l025[ff]]l025fffl025[[]r025]r025fff[r02
    5fff]l025[ff][ffl090ff]"""

    assert test_chaos(3)[0] == """[fff[l090f][r090f]f]r090[fff[l090f][r090f]f]r
    090[fff[l090f][r090f]f]r090[fff[l090f][r090f]f][[l090f][r090f]f]r090[[l090f
    ][r090f]f]r090[[l090f][r090f]f]r090[[l090f][r090f]f]"""

    # Recursion tasks
    assert line_recursive(6) == "ffffffffffffffffffffffffffffffff"

    assert koch_curve_recursive(3) == """fl045fr045r045fl045fl045fl045fr045r045
    fl045fr045r045fl045fr045r045fl045fl045fl045fr045r045fl045f"""

    assert sierpinsky_triangle_recursive(3) == """fl120fr120fr120fl120fl120ffr1
    20fl120fr120fr120fl120fr120ffl120fl120fr120fr120fl120fl120ffffl120ffff"""

    assert harder_recursive(3) == """ffffffl025[[fffl025[[]r025]r025fff[r025fff
    ]l025[ff]]r025fffl025[[]r025]r025fff[r025fff]l025[ff]]r025ffffff[r025ffffff
    fffl025[[]r025]r025fff[r025fff]l025[ff]]l025fffl025[[]r025]r025fff[r025fff]
    l025[ff][ffl090ff]"""


if __name__ == "__main__":
    # line_recursive(6)
    # test_koch(5)
    # test_sierpinsky_triangle(3)
    # test_barley_deterministic(6)
    # test_barley_non_deterministic(2, 5)
    # test_harder_recursive(6)
    # test_harder_recursive(3)
    basic_tests()
    pass
