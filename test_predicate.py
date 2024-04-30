from predicate import *


def test_Field():
    assert Field("foo").evaluate() == "foo"


def test_Field_parse_json():
    data = '{"expression_type": "Field", "value": "foo"}'
    field = Field.parse_json(data)
    assert field == Field("foo")


def test_Literal():
    assert Literal(7).evaluate() == "7"
    assert Literal("foo").evaluate() == "'foo'"
    assert Literal(7.7).evaluate() == "7.7"
    assert Literal(True).evaluate() == "True"


def test_Literal_parse_json():
    # fmt: off
    assert Literal.parse_json('{"expression_type": "Literal", "value": 7}') == Literal(7)
    assert Literal.parse_json('{"expression_type": "Literal", "value": "foo"}') == Literal("foo")
    assert Literal.parse_json('{"expression_type": "Literal", "value": 7.7}') == Literal(7.7)
    assert Literal.parse_json('{"expression_type": "Literal", "value": true}') == Literal(True)
    # fmt: on


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


def test_BinaryOperation_parse_json():
    # fmt: off
    actual = BinaryOperation.parse_json('''\
    {
        "expression_type": "BinaryOperation",
        "op" : "AND",
        "lhs" : {"expression_type": "Field", "value": "A"},
        "rhs" : {"expression_type": "Literal", "value": 7}
    }
    ''')
    # fmt: on
    f1 = Field("A")
    f2 = Field("B")
    v1 = Literal(7)
    v2 = Literal(7.7)
    expected = BinaryOperation(BinaryOperator.AND, f1, v1)
    assert expected == actual


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
