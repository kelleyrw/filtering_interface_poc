from abc import ABC, abstractmethod
from enum import Enum


class Operator(Enum):
    OR: str = "or"
    AND: str = "and"
    NOT: str = "not"
    EQUAL: str = "="


class Expression(ABC):

    @abstractmethod
    def evaluate(self) -> str:
        pass


class BinaryOperatorExpression:
    def __init__(self, lhs: Expression, op: Operator, rhs: Expression):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self) -> str:
        return f"({self.lhs.evaluate()}) {self.op} ({self.rhs.evaluate()})"


class Literal(Expression):
    def __init__(self, value: int | float | str) -> None:
        self.value = str(value)

    def evaluate(self) -> str:
        return self.value


def LogicalEqual(lhs: Expression, rhs: Expression) -> BinaryOperatorExpression:
    return BinaryOperatorExpression(lhs, Operator.EQUAL.value, rhs)


def test_Literal():
    l = Literal(7)
    assert l.evaluate() == "7"


def test_EqualExpression(subtests):
    v1 = Literal(7)
    f1 = Literal("A")
    with subtests.test(msg="(A) = (7)"):
        eq1 = LogicalEqual(f1, v1)
        assert eq1.evaluate() == "(A) = (7)"
    with subtests.test(msg="((7) = (A)"):
        eq1 = LogicalEqual(v1, f1)
        assert eq1.evaluate() == "(7) = (A)"
    with subtests.test(msg="(A) = (A)"):
        eq1 = LogicalEqual(f1, f1)
        assert eq1.evaluate() == "(A) = (A)"
    with subtests.test(msg="(7) = (7)"):
        eq1 = LogicalEqual(v1, v1)
        assert eq1.evaluate() == "(7) = (7)"

    with subtests.test(msg="(A = 7) = (B = 42)"):
        f2 = Literal("B")
        v2 = Literal("42")
        eq1 = LogicalEqual(f1, v1)
        eq2 = LogicalEqual(f2, v2)
        compound = LogicalEqual(eq1, eq2)
        assert compound.evaluate() == "((A) = (7)) = ((B) = (42))"


# @pytest.fixture()
# def trival():
#     value = dict(operator="=", field="A", value="7")
#     return value
#
#
# def test_foo(trival):
#     print(trival)
#     assert True
