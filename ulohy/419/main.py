#!/usr/bin/env python3

# Tuto funkci implementuj.
def penguins_in_group(total: int, group_size: int) -> int:
    if total < group_size:
        return 0
    return 1 + penguins_in_group(total - group_size, group_size)

# Testy:
print("Máme 20 tučniakov, potrebujeme 5 tímov, v jednom tíme bude musieť byť ",penguins_in_group(20, 5))  # 4
print(penguins_in_group(392, 4))  #98

def my_abacus(base: int, exp: int) -> int:
    if exp != 0:
        return multiply(my_abacus(base, exp - 1), base)
    else:
        return 1

def multiply(a: int, b: int) -> int:
    mul = 0
    for i in range(b):
        mul += a
    return mul

# Testy:
print(my_abacus(10, 2))  # 100
print(my_abacus(34, 3))  # 39 304
print(my_abacus(8, 5))  # 32 768
print(my_abacus(2, 10))  # 1024

