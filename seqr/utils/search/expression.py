from textwrap import indent
from typing import List, Optional, Dict, Tuple, Union, Type, Iterable, Collection, Sequence

from enum import Enum
from abc import ABC, abstractmethod

INDENT = " "


def quote_value(value):
    if isinstance(value, str):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


class ExpressionType(Enum):
    FIELD = 1
    LITERAL = 2
    CALL = 3


class Expression(ABC):
    def __init__(self, _type: ExpressionType) -> None:
        self.type = _type

    @abstractmethod
    def to_python(self) -> str:
        pass

    @abstractmethod
    def to_protobuf(self) -> str:
        pass

    @abstractmethod
    def to_elasticsearch(self) -> Dict[str, any]:
        pass

    @abstractmethod
    def to_sql(self):
        pass

    def output_sql(self, tablename: str, fields: str = '*'):
        if isinstance(fields, list):
            fields = ', '.join(fields)

        expr = self.to_sql()
        return f'SELECT {fields} FROM {tablename} WHERE {expr}'

    def output_elasticsearch(self, sort: List[str], from_: int, size: int, source: List[str]):
        query = self.to_elasticsearch()
        if isinstance(query, list):
            query = {'filter': query}
        return {
            'query': {'bool': query},
            'sort': sort,
            'from': from_,
            'size': size,
            '_source': source
        }

    def output_protobuf(
        self, fields: List[str], arrow_urls: List[str], max_rows=10000
    ) -> str:

        headers = []
        # arrow links
        headers.extend(f'arrow_urls: "{url}"' for url in arrow_urls)

        # fields to select
        headers.extend(f'projection_columns: "{col}"' for col in fields)
        str_headers = "\n".join(headers)

        return f"""\
{str_headers}

filter_expression {{
{indent(self.to_protobuf(), INDENT)}
}}

max_rows: {10000}
"""

    # helpers
    def or_(self, expression: 'Expression'):
        return CallOr(self, expression)

    def and_(self, expression: 'Expression'):
        return CallAnd(self, expression)

    def negate(self):
        return CallNegate(self)



class Field(Expression):
    def __init__(self, name: str):
        super().__init__(ExpressionType.FIELD)
        self.name = name

    def to_protobuf(self) -> str:
        return f'column: "{self.name}"'

    def to_elasticsearch(self) -> Dict[str, any]:
        return self.name

    def to_sql(self):
        return self.name

    def to_python(self):
        return f'Field(name="{self.name}")'


class Literal(Expression):
    def __init__(self, literal: any, literal_type: Optional[str]=None):
        super().__init__(ExpressionType.LITERAL)
        self.literal = literal
        self.protobuf_type = literal_type or self.infer_protobuf_type(literal)

    def to_python(self):
        literal = self.literal
        if isinstance(self.literal, str):
            literal = quote_value(literal)

        return f'Literal(literal={literal}, literal_type="{self.protobuf_type}")'

    def to_elasticsearch(self) -> any:
        return quote_value(self.literal) if isinstance(self.literal, str) else self.literal

    def to_sql(self):
        return quote_value(self.literal) if isinstance(self.literal, str) else self.literal

    def to_protobuf(self) -> str:
        literal_value = self.literal
        if self.protobuf_type == "string_value":
            escaped = literal_value.replace('"', '\\"')
            literal_value = f'"{escaped}"'

        return f"""\
literal {{
{INDENT}{self.protobuf_type}: {literal_value}
}}"""

    @staticmethod
    def infer_protobuf_type(literal: any):
        if isinstance(literal, str):
            return "string_value"
        if isinstance(literal, int):
            # 32 bit: https://stackoverflow.com/a/49049072
            if abs(literal) <= 0xFFFFFFFF:
                return "int32_value"
            return "int64_value"
        if isinstance(literal, float):
            # python 'float' is dependent on system, but is usually 64 bits
            # import sys,math; print(sys.float_info.mant_dig + math.ceil(math.log2(sys.float_info.max_10_exp - sys.float_info.min_10_exp)) + 1)
            return "double_value"
        if isinstance(literal, bool):
            return "bool_value"

class Call(Expression, ABC):
    def __init__(
        self,
        *arguments,
        protobuf_options: Dict[str, List[Tuple[str, any]]] = None,
        **kwargs,
    ):
        if any(a is None for a in arguments):
            raise ValueError('An argument was None')
        if not isinstance(arguments, (tuple, list)):
            raise ValueError(
                f"Expected arguments to be a list, received: {type(arguments)}"
            )
        if len(arguments) == 0:
            raise ValueError('Expected at least 1 argument')

        self.arguments = arguments
        self.protobuf_options = protobuf_options
        self.kwargs = kwargs

    def to_python(self):
        args = []
        if self.arguments:
            args.extend(a.to_python() if isinstance(a, Expression) else a for a in self.arguments)
        if self.protobuf_options:
            args.append(f'protobuf_options={self.protobuf_options}')
        if self.kwargs:
            args.extend(f'{k}={v}' for k,v in self.kwargs)
        sargs = ', '.join(args)
        return f'{self.__class__.__name__}({sargs})'

    @abstractmethod
    def protobuf_call_name(self):
        # should be a function_name declared in:
        # https://arrow.apache.org/docs/cpp/compute.html
        raise NotImplementedError

    def to_protobuf(self) -> str:

        _str_arguments = "\n".join(
            f"""\
arguments {{
{indent(a.to_protobuf(), INDENT)}
}}"""
            for a in self.arguments
        )

        internals = [f'function_name: "{self.protobuf_call_name()}"', _str_arguments]

        options = self.protobuf_options
        if options:
            # they need to be quoted
            for k, d in options.items():
                inner = "\n".join(f"{kk}: {vv}" for kk, vv in d)
                internals.append(f"{k} {{\n{indent(inner, INDENT)}\n}}")

        str_internals = indent("\n".join(internals), INDENT)
        return f"call {{\n{str_internals}\n}}"


# Function definitions

class MaxTwoArgumentsCall(Call, ABC):
    @classmethod
    def split_into_calls_of_two(cls: Type['Call'], iterable: Sequence[Expression]):
        if len(iterable) == 0:
            return None
        if len(iterable) == 1:
            return iterable[0]

        call = cls(*iterable[-2:])
        for i in range(len(iterable) - 3, -1, -1):
            call = cls(iterable[i], call)

        return call

    def to_protobuf(self) -> str:
        if len(self.arguments) == 2:
            return super().to_protobuf()
        expr = self.split_into_calls_of_two(self.arguments)
        return expr.to_protobuf()


class CallAnd(MaxTwoArgumentsCall):
    def protobuf_call_name(self):
        return 'and'

    def to_sql(self):
        return '(' + ' AND '.join(a.to_sql() for a in self.arguments) + ')'

    def to_elasticsearch(self) -> Dict[str, any]:
        return {'must': [a.to_elasticsearch() for a in self.arguments]}


class CallOr(MaxTwoArgumentsCall):
    def protobuf_call_name(self):
        return 'or'

    def to_elasticsearch(self) -> Dict[str, any]:
        return {'should': [a.to_elasticsearch() for a in self.arguments], 'minimum_should_match': 1}

    def to_sql(self):
        return '(' + ' OR '.join(a.to_sql() for a in self.arguments) + ')'


class CallNegate(Call):
    def __init__(self, argument: Expression):
        super().__init__(argument)

    def protobuf_call_name(self):
        return "invert"

    def to_sql(self):
        return f'NOT {self.arguments[0].to_sql()}'

    def to_elasticsearch(self) -> Dict[str, any]:
        return {'negate': self.arguments[0].to_elasticsearch()}


class CallIsNotNull(Call):
    def __init__(self, argument: Expression):
        super().__init__(argument)

    def protobuf_call_name(self):
        return "is_valid"

    def to_sql(self):
        return f'{self.arguments[0].to_sql()} IS NOT NULL'


class CallExists(Call):
    def __init__(self, argument: Field):
        super().__init__(argument)

    def protobuf_call_name(self):
        return 'is_valid'

    def to_sql(self):
        return f'{self.arguments[0].to_sql()} IS NOT NULL'


class CallEqual(Call):
    def protobuf_call_name(self):
        return "equal"

    def to_elasticsearch(self) -> Dict[str, any]:
        lhs, rhs = self.arguments
        if not isinstance(rhs, Literal) or not isinstance(lhs, Field):
            raise ValueError(
                'Only know how to compare CallEqual with Field == Literal, '
                f'got {type(lhs)} == {type(rhs)}'
            )

        return {'term': {lhs.name: rhs.literal}}

    def to_sql(self):
        lhs, rhs = (a.to_sql() for a in self.arguments)

        return f'{lhs} = {rhs}'



class CallNotEqual(Call):
    def protobuf_call_name(self):
        return "not_equal"

    def to_sql(self):
        lhs, rhs = (a.to_sql() for a in self.arguments)

        return f'{lhs} != {rhs}'


class CallLessThan(Call):
    def protobuf_call_name(self):
        return "less"

    def to_sql(self):
        lhs, rhs = (a.to_sql() for a in self.arguments)

        return f'{lhs} < {rhs}'


class CallGreaterThan(Call):
    def protobuf_call_name(self):
        return "greater"

    def to_sql(self):
        lhs, rhs = (a.to_sql() for a in self.arguments)

        return f'{lhs} > {rhs}'


class CallLessThanOrEqual(Call):
    def protobuf_call_name(self):
        return "less_equal"

    def to_sql(self):
        lhs, rhs = (a.to_sql() for a in self.arguments)

        return f'{lhs} <= {rhs}'

    def to_elasticsearch(self) -> Dict[str, any]:
        col, value = self.arguments
        return {'range': {col.name: {'lte': value.literal}}}


class CallGreaterEqual(Call):
    def protobuf_call_name(self):
        return "greater_equal"

    def to_sql(self):
        lhs, rhs = (a.to_sql() for a in self.arguments)

        return f'{lhs} >= {rhs}'


class CallFieldIsOneOf(Call):
    def __init__(self, field: Field, values: List[Union[int, str, float]]):
        prepped_values = [("values", quote_value(v)) for v in values]

        super().__init__(
            field, protobuf_options={"set_lookup_options": prepped_values}
        )

        self.values = values

    def to_python(self):
        return f'{self.__class__.__name__}(field={self.arguments[0].to_python()}, values={self.values})'

    def protobuf_call_name(self):
        return "is_in"

    def to_elasticsearch(self) -> Dict[str, any]:
        return {'terms': {self.arguments[0].name: self.values}}

    def to_sql(self):
        a = self.arguments[0].to_sql()
        values = ', '.join(quote_value(v) if isinstance(v, str) else v for v in self.values)

        return f'{a} in ({values})'


class CallFieldListContains(Call):
    def __init__(self, field: Field, value: Union[str, int, float]):
        super().__init__(
            field,
            protobuf_options={"set_lookup_options": [("values", quote_value(value))]},
        )

        self.values = value

    def to_python(self):
        return f'{self.__class__.__name__}(field={self.arguments[0].to_python()}, values={self.values})'

    def protobuf_call_name(self):
        return "string_list_contains_any"

    def to_elasticsearch(self) -> Dict[str, any]:
        return {'terms': {self.arguments[0].name: self.values}}

    def to_sql(self):
        a = self.arguments[0].to_sql()
        values = ', '.join(self.values)

        # this isn't valid because you nested structures don't exist in SQL
        return f'{a} in ({values})'
