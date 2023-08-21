# Based off of examples/generators/outputs/PythonAST.py from pyasdl
from __future__ import annotations

import typing
from dataclasses import dataclass

# Base classes

class AST:
    start_lineno: int
    end_lineno: int | None

class expression(AST):
    ...

class statement(AST):
    ...

class exception_handler(AST):
    ...

# Base Types

class array(str):
    ...

class address(str):
    ...

class backtick_expression(str):
    ...

class hashtable(str):
    ...

class identifier(str):
    ...

class java_class(str):
    ...

class literal(str):
    ...

class long(int):
    ...

class object_expression(str):
    ...

class scalar(str):
    ...

constant = typing.Union[
    address,
    backtick_expression,
    bool,
    float,
    int,
    java_class,
    literal,
    long,
    object_expression,
    str,
    None
]


lvalue = typing.Union[
    array,
    hashtable,
    scalar
]

rvalue = typing.Union[
    constant,
    lvalue
]

# High level classes

@dataclass
class Arg(AST):
    name: str | expression | None
    value: expression
    
@dataclass
class Block(AST):
    body: list[statement]

@dataclass
class KvPair(AST):
    name: expression
    value: expression

@dataclass
class Script(AST):
    body: list[statement]

# Commands

@dataclass
class Break(statement):
    ...

@dataclass
class Callcc(statement):
    closure: object

@dataclass
class Continue(statement):
    ...

@dataclass
class Done(statement):
    ...

@dataclass
class Halt(statement):
    ...

@dataclass
class Import(statement):
    target: str

@dataclass
class ImportFrom(statement):
    target: str
    path: str

@dataclass
class Return(statement):
    value: expression | None

@dataclass
class Throw(statement):
    value: expression

@dataclass
class Yield(statement):
    value: expression | None

# Flow control

@dataclass
class Assert(statement):
    test: expression
    message: expression | None


@dataclass
class Catch(exception_handler):
    value: object
    body: list[statement]

@dataclass
class EnvBridge(statement):
    keyword: str
    identifier: str | None
    string: str | None
    body: list[statement]

@dataclass
class For(statement):
    initializer: list[expression]
    test: expression
    increment: list[expression]
    body: list[statement]

@dataclass
class Foreach(statement):
    index: str | None
    value: str
    generator: expression
    body: list[statement]

@dataclass
class If(statement):
    test: expression
    body: list[statement]
    orelse: list[statement]

@dataclass
class Try(statement):
    body: list[statement]
    handler: exception_handler

@dataclass
class While(statement):
    test: expression
    body: list[statement]

# Expressions

@dataclass
class Call(expression):
    function: str
    args: list[Arg]

@dataclass
class BinOp(expression):
    left: expression
    op: str
    right: expression

@dataclass
class Constant(expression):
    value: lvalue | rvalue

@dataclass
class Index(expression):
    container: expression
    element: expression

@dataclass
class UnaryOp(expression):
    op: str
    operand: expression