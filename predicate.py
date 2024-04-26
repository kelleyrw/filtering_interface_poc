from abc import ABC, abstractmethod
from enum import Enum

__ALL__ = [
    "Field",
    "Logical",
    "BinaryOperator",
]

# ---------------------------------------------------------------------------- #
# Errors
# ---------------------------------------------------------------------------- #


class UnsupportedTypeError(Exception):
    pass


# ---------------------------------------------------------------------------- #
# Expressions
# ---------------------------------------------------------------------------- #


class Expression(ABC):

    @abstractmethod
    def evaluate(self) -> str:
        pass

    # @abstractmethod
    # def from_json(self) -> str:
    #     pass
    #
    # @abstractmethod
    # def to_json(self) -> str:
    #     pass


class Field(Expression):
    def __init__(self, value) -> None:
        self.value = value

    @classmethod
    def from_json(cls, json_value):
        pass

    def evaluate(self) -> str:
        return self.value


class Literal(Expression):
    def __init__(self, value: int | float | str | bool) -> None:
        self.value = value

    def evaluate(self) -> str:
        # todo: make this more resilient to the various flavors of ints ad floats
        if isinstance(self.value, int) or isinstance(self.value, float):
            result = str(self.value)

        # todo: make this more resilient to the various flavors of strings
        elif isinstance(self.value, str):
            result = f"'{self.value}'"

        # SQL booleans are lowercase
        elif isinstance(self.value, bool):
            result = str(self.value).lower()

        # SQL booleans are lowercase
        elif isinstance(self.value, bool):
            result = str(self.value).lower()

        else:
            raise UnsupportedTypeError(f"type {type(self.value)} not supported")

        return result


# ---------------------------------------------------------------------------- #
# Binary Operator
# ---------------------------------------------------------------------------- #


class BinaryOperator(Enum):
    EQUAL: str = "="
    NOTEQUAL: str = "="
    AND: str = "and"
    OR: str = "or"
    LT: str = "<"
    LTE: str = "<="
    GT: str = ">"
    GTE: str = ">="


class BinaryOperation(Expression):
    def __init__(
        self,
        op: BinaryOperator,
        lhs: Expression | str | float | int | bool,
        rhs: Expression | str | float | int | bool,
    ):
        self.op = op
        self.lhs = lhs if isinstance(lhs, Expression) else Literal(lhs)
        self.rhs = rhs if isinstance(rhs, Expression) else Literal(rhs)

    def evaluate(self) -> str:
        return f"({self.lhs.evaluate()}) {self.op.value} ({self.rhs.evaluate()})"


def LogicalEqual(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.EQUAL, lhs, rhs)


def LogicalNotEqual(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.NOTEQUAL, lhs, rhs)


def LogicalAND(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.AND, lhs, rhs)


def LogicalOR(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.OR, lhs, rhs)


def LogicalLT(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.LT, lhs, rhs)


def LogicalLTE(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.LTE, lhs, rhs)


def LogicalGT(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.GT, lhs, rhs)


def LogicalGTE(lhs: Expression, rhs: Expression) -> BinaryOperation:
    return BinaryOperation(BinaryOperator.GTE, lhs, rhs)


# ---------------------------------------------------------------------------- #
# Unary Operator
# ---------------------------------------------------------------------------- #


class UnaryPrefixOperator(Enum):
    NOT: str = "not"


class UnaryPrefixOperation(Expression):
    def __init__(
        self,
        op: UnaryPrefixOperator,
        value: Expression | str | float | int | bool,
    ):
        self.op = op
        self.value = value if isinstance(value, Expression) else Literal(value)

    def evaluate(self) -> str:
        return f"{self.op.value} ({self.value.evaluate()})"


def LogicalNot(value: Expression) -> UnaryPrefixOperator:
    return UnaryPrefixOperator(UnaryPrefixOperator.NOT, value)


# ---------------------------------------------------------------------------- #
# Predicate
# ---------------------------------------------------------------------------- #


class Predicate:

    def __init__(self, predicate: Expression):
        self.predicate = predicate

    @classmethod
    def from_json(cls, value: dict) -> "Predicate":
        return Expression.from_json(value)

    def evaluate(self) -> str:
        result = self.predicate.evaluate()


# ---------------------------------------------------------------------------- #
# tests
# ---------------------------------------------------------------------------- #


def test_Field():
    assert Field("foo").evaluate() == "foo"


def test_Literal():
    assert Literal(7).evaluate() == "7"
    assert Literal("foo").evaluate() == "'foo'"
    assert Literal(7.7).evaluate() == "7.7"
    assert Literal(True).evaluate() == "True"


def test_BinaryOperation(subtests):
    f1 = Field("A")
    f2 = Field("B")
    v1 = Literal(7)
    v2 = Literal(7.7)
    for op in [
        BinaryOperator.NOTEQUAL,
        BinaryOperator.EQUAL,
        BinaryOperator.AND,
        BinaryOperator.OR,
        BinaryOperator.LT,
        BinaryOperator.LTE,
        BinaryOperator.GT,
        BinaryOperator.GTE,
    ]:
        with subtests.test(msg=f"operator {op.value}"):
            # basic
            assert BinaryOperation(op, f1, v1).evaluate() == f"(A) {op.value} (7)"
            assert BinaryOperation(op, v1, f1).evaluate() == f"(7) {op.value} (A)"
            assert BinaryOperation(op, f1, f1).evaluate() == f"(A) {op.value} (A)"
            assert BinaryOperation(op, v1, v1).evaluate() == f"(7) {op.value} (7)"

            # compound
            eq1 = LogicalEqual(f1, v1)
            eq2 = LogicalEqual(f2, v2)
            compound = BinaryOperation(op, eq1, eq2)
            assert compound.evaluate() == f"((A) = (7)) {op.value} ((B) = (7.7))"


def test_UnaryPrefixOperation(subtests):
    f1 = Field("A")
    f2 = Field("B")
    v1 = Literal(7)
    v2 = Literal(7.7)
    op = UnaryPrefixOperator.NOT

    # basic
    assert UnaryPrefixOperation(op, f1).evaluate() == f"{op.value} (A)"
    assert UnaryPrefixOperation(op, v1).evaluate() == f"{op.value} (7)"

    # compound
    eq1 = LogicalEqual(f2, v2)
    compound = UnaryPrefixOperation(op, eq1)
    assert compound.evaluate() == f"{op.value} ((B) = (7.7))"


# @pytest.fixture()
# def trival():
#     value = dict(operator="=", field="A", value="7")
#     return value
#
#
# def test_foo(trival):
#     print(trival)
#     assert True
