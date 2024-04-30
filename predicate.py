from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel
from pydantic_core import from_json

__ALL__ = [
    "Field",
    "Logical",
    "BinaryOperator",
    "UnaryPrefixOperator",
]

# ---------------------------------------------------------------------------- #
# Errors
# ---------------------------------------------------------------------------- #


class UnsupportedTypeError(Exception):
    pass


# ---------------------------------------------------------------------------- #
# parsing models (not public facing)
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
# Expressions
# ---------------------------------------------------------------------------- #


class Expression(ABC):

    @abstractmethod
    def evaluate(self) -> str:
        pass

    # class _ExpressionParseBase(BaseModel):
    #     expression_type: str

    # @abstractmethod
    # def from_json(self) -> str:
    #     pass

    # @abstractmethod
    # def to_json(self) -> str:
    #     pass


class Field(Expression):
    def __init__(self, value) -> None:
        self.value = value

    def evaluate(self) -> str:
        return self.value

    def __eq__(self, other):
        return isinstance(other, Field) and self.value == other.value

    @classmethod
    def parse_json(cls, json_value):
        args: dict = from_json(json_value, allow_partial=True)
        args.pop("expression_type", None)
        return cls(**args)


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

    @classmethod
    def parse_json(cls, json_value):
        args: dict = from_json(json_value, allow_partial=True)
        args.pop("expression_type", None)
        return cls(**args)

    def __eq__(self, other):
        return isinstance(other, Literal) and self.value == other.value


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
        op: BinaryOperator | str,
        lhs: Expression | str | float | int | bool,
        rhs: Expression | str | float | int | bool,
    ):
        self.op = op if isinstance(op, BinaryOperator) else BinaryOperator[op]
        self.lhs = lhs if isinstance(lhs, Expression) else Literal(lhs)
        self.rhs = rhs if isinstance(rhs, Expression) else Literal(rhs)

    def evaluate(self) -> str:
        return f"({self.lhs.evaluate()}) {self.op.value} ({self.rhs.evaluate()})"

    @classmethod
    def parse_json(cls, json_value):
        args: dict = from_json(json_value, allow_partial=True)
        op = BinaryOperator[args["op"]]
        lhs = cls.ExpressionParser.parse_json(args["lhs"])
        rhs = cls.ExpressionParser.parse_json(args["rhs"])

    def __eq__(self, other):
        return (
            isinstance(other, BinaryOperation)
            and self.op == other.op
            and self.lhs == other.lhs
            and self.rhs == other.rhs
        )


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

    # @classmethod
    # def from_json(cls, value: dict) -> "Predicate":
    #     return Expression.from_json(value)
    #
    # def evaluate(self) -> str:
    #     result = self.predicate.evaluate()
