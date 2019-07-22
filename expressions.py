from typing import Any
from typing import Union

from utils import KQL
from utils import KustoTypes, to_kql

ExpressionTypes = Union[KustoTypes, 'BaseExpression', 'Column']
StringTypes = Union[str, 'StringExpression', 'Column']
BooleanTypes = Union[bool, 'BooleanExpression', 'Column']
NumberTypes = Union[int, float, 'NumberExpression', 'Column']


class BaseExpression:
    kql: KQL

    def __init__(self, kql: KQL) -> None:
        self.kql = kql

    def as_subexpression(self) -> KQL:
        return KQL('({})'.format(self.kql))

    @staticmethod
    def _subexpression_to_kql(obj: ExpressionTypes) -> KQL:
        if isinstance(obj, BaseExpression):
            return obj.as_subexpression()
        return to_kql(obj)

    def __eq__(self, other: ExpressionTypes) -> 'BooleanExpression':
        return BooleanExpression.bi_operator(self, ' == ', other)

    def __ne__(self, other: ExpressionTypes) -> 'BooleanExpression':
        return BooleanExpression.bi_operator(self, ' != ', other)

    def is_in(self, other: ExpressionTypes) -> 'BooleanExpression':
        return BooleanExpression.bi_operator(self, ' in ', other)

    def __contains__(self, other: Any) -> bool:
        """
        Deliberately not implemented, because "not in" inverses the result of this method, and there is no way to
        override it
        """
        raise ValueError()  # Not raising NotImplementedError because then subclasses will be required to override it


class BooleanExpression(BaseExpression):
    @staticmethod
    def bi_operator(left: ExpressionTypes, operator: str, right: ExpressionTypes) -> 'BooleanExpression':
        return BooleanExpression(
            KQL('{}{}{}'.format(left._subexpression_to_kql(left), operator, right._subexpression_to_kql(right)))
        )

    def __and__(self, other: BooleanTypes) -> 'BooleanExpression':
        return BooleanTypes(self, ' and ', other)


class NumberExpression(BaseExpression):
    @staticmethod
    def bi_operator(left: NumberTypes, operator: str, right: NumberTypes) -> 'NumberExpression':
        return NumberExpression(
            KQL('{}{}{}'.format(left._subexpression_to_kql(left), operator, right._subexpression_to_kql(right)))
        )

    def __lt__(self, other: NumberTypes) -> BooleanExpression:
        return BooleanExpression.bi_operator(self, ' < ', other)

    def __le__(self, other: NumberTypes) -> BooleanExpression:
        return BooleanExpression.bi_operator(self, ' <= ', other)

    def __gt__(self, other: NumberTypes) -> BooleanExpression:
        return BooleanExpression.bi_operator(self, ' > ', other)

    def __ge__(self, other: NumberTypes) -> BooleanExpression:
        return BooleanExpression.bi_operator(self, ' >= ', other)

    def __add__(self, other: NumberTypes) -> 'NumberExpression':
        return NumberExpression.bi_operator(self, ' + ', other)

    def __sub__(self, other: NumberTypes) -> 'NumberExpression':
        return NumberExpression.bi_operator(self, ' - ', other)

    def __mul__(self, other: NumberTypes) -> 'NumberExpression':
        return NumberExpression.bi_operator(self, ' * ', other)

    def __truediv__(self, other: NumberTypes) -> 'NumberExpression':
        return NumberExpression.bi_operator(self, ' / ', other)

    def __mod__(self, other: NumberTypes) -> 'NumberExpression':
        return NumberExpression.bi_operator(self, ' % ', other)


class StringExpression(BaseExpression):
    def __len__(self) -> NumberExpression:
        return NumberExpression(KQL('string_size({})'.format(self.kql)))
