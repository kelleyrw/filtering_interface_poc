import json
from enum import Enum

import pytest


class Operator(Enum):
    OR: str = "or"
    AND: str = "and"
    NOT: str = "not"
    EQUAL: str = "eq"


class Expression:

    def evaluate(self) -> str:
        pass


class Literal(Expression):
    def __init__(self, value: int | float | str) -> None:
        self.value = str(value)

    def evaluate(self) -> str:
        return self.value


class EqualExpression(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self) -> str:
        return f"{self.lhs.evaluate()} = {self.rhs.evaluate()}"


class ORExpression(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self) -> str:
        return f"{self.lhs.evaluate()} or {self.rhs.evaluate()}"


def test_Literal():
    l = Literal(7)
    assert l.evaluate() == "7"


def test_EqualExpression(subtests):
    v1 = Literal(7)
    f1 = Literal("A")
    with subtests.test(msg="A = 7"):
        eq1 = EqualExpression(f1, v1)
        assert eq1.evaluate() == "A = 7"
    with subtests.test(msg="7 = A"):
        eq1 = EqualExpression(v1, f1)
        assert eq1.evaluate() == "7 = A"
    with subtests.test(msg="A = A"):
        eq1 = EqualExpression(f1, f1)
        assert eq1.evaluate() == "A = A"
    with subtests.test(msg="7 = 7"):
        eq1 = EqualExpression(v1, v1)
        assert eq1.evaluate() == "7 = 7"

    with subtests.test(msg="7 = 7"):
        f2 = Literal("B")
        v2 = Literal("42")
        eq1 = EqualExpression(f1, v1)
        eq2 = EqualExpression(f2, v2)
        compound = ORExpression(eq1, eq2)
        assert compound.evaluate() == "A = 7 or B = 42"


# class Filter:
#     def __init__(self, expression: Expression):
#         self.expression = expression
#
#     def evaluate(self) -> str:
#         self.exp


@pytest.fixture()
def trival():
    value = dict(operator="=", field="A", value="7")
    return value


def test_foo(trival):
    print(trival)
    assert True
