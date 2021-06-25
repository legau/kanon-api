import re
from operator import add, mul, sub, truediv
from typing import Any, Callable, Type

from kanon.units import BasedReal

OPERATORS: dict[str, Callable[[Any, Any], Any]] = {
    "+": add,
    "-": sub,
    "*": mul,
    "/": truediv,
}

BRMATCHER = re.compile(r"^(([0-9]*),)*[0-9]+(;(([0-9]*),)*[0-9]+)? *$")

SIGNMATCHER = re.compile(r"([\+\-]+)")


def parse(input: str, br: Type[BasedReal], trace="") -> BasedReal:
    if not trace:
        input = input.replace(" ", "")
        signs = SIGNMATCHER.findall(input)
        for s in signs:
            parity = (len(s) - s.count("+")) % 2
            input = input.replace(s, "-" if parity else "+", 1)
    for token, op in OPERATORS.items():
        if token in input:
            a, b = input.split(token, 1)
            if a == "":
                if token == "-":
                    return -parse(b, br, input)
                elif token == "+":
                    return parse(b, br, input)
            return op(parse(a, br, input), parse(b, br, input))
    if BRMATCHER.match(input):
        split = input.partition(";")
        left = tuple(int(n) for n in split[0].split(","))
        right = tuple(int(n) for n in split[2].split(",") if n)

        return br(left, right)
    raise SyntaxError(f"Invalid syntax : {trace or input}")
