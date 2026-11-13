"""Interactive arithmetic calculator using only the Python standard library."""

import math
import re
import sys


NUMBER = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "u+": 3, "u-": 3}


class CalculationError(ValueError):
    """An expression is outside the supported arithmetic grammar."""


def apply_operator(values, operator):
    if operator in ("u+", "u-"):
        value = values.pop()
        result = value if operator == "u+" else -value
    else:
        right = values.pop()
        left = values.pop()
        if operator == "+":
            result = left + right
        elif operator == "-":
            result = left - right
        elif operator == "*":
            result = left * right
        else:
            if right == 0:
                raise CalculationError("деление на ноль")
            result = left / right
    if isinstance(result, float) and not math.isfinite(result):
        raise CalculationError("число выходит за допустимый диапазон")
    values.append(result)


def evaluate(expression):
    """Parse numbers and arithmetic operators without executing Python code.

    Explicit stacks keep nested parentheses and unary signs independent of
    Python's recursion limit. Binary operators are left-associative.
    """
    if not expression.strip():
        raise CalculationError("пустое выражение")

    values = []
    operators = []
    expecting_operand = True
    position = 0
    while position < len(expression):
        character = expression[position]
        if character.isspace():
            position += 1
            continue

        if expecting_operand:
            if character in "+-":
                operators.append("u" + character)
            elif character == "(":
                operators.append(character)
            else:
                match = NUMBER.match(expression, position)
                if match is None:
                    raise CalculationError("ожидалось число, унарный знак или скобка")
                literal = match.group()
                value = float(literal) if "." in literal else int(literal)
                if isinstance(value, float) and not math.isfinite(value):
                    raise CalculationError("число выходит за допустимый диапазон")
                values.append(value)
                expecting_operand = False
                position = match.end()
                continue
        elif character in "+-*/":
            while (operators and operators[-1] != "("
                   and PRECEDENCE[operators[-1]] >= PRECEDENCE[character]):
                apply_operator(values, operators.pop())
            operators.append(character)
            expecting_operand = True
        elif character == ")":
            while operators and operators[-1] != "(":
                apply_operator(values, operators.pop())
            if not operators:
                raise CalculationError("лишняя закрывающая скобка")
            operators.pop()
        else:
            raise CalculationError("ожидался арифметический оператор или закрывающая скобка")
        position += 1

    if expecting_operand:
        raise CalculationError("выражение не завершено: ожидалось число")
    while operators:
        operator = operators.pop()
        if operator == "(":
            raise CalculationError("пропущена закрывающая скобка")
        apply_operator(values, operator)
    return values[0]


def main():
    if len(sys.argv) != 1:
        print("Ошибка: аргументы не поддерживаются; запуск: python3 calc.py", file=sys.stderr)
        return 1

    prompt = "> " if sys.stdin.isatty() else ""
    while True:
        try:
            expression = input(prompt)
        except EOFError:
            return 0
        if expression.strip() == "exit":
            return 0
        try:
            result = evaluate(expression)
            print(result)
        except CalculationError as error:
            print(f"Ошибка: {error}", file=sys.stderr)
        except (OverflowError, ValueError):
            print("Ошибка: число выходит за допустимый диапазон", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
