# -*- coding: utf-8 -*-

from __future__ import annotations

import typing
from dataclasses import dataclass

eol = '\n'
indention = '    '

# Base classes

class AST:
    start_lineno: int
    end_lineno: int | None

class exception_handler(AST):
    ...

class flow_control(AST):
    ...

class command(AST):
    ...

class expression(command):
    ...

_format_expression = lambda value: value.format() if isinstance(value, expression) else str(value)

# Base Types

class address(str):
    ...

class array(str):
    ...

class backtick_expression(str):
    def __str__(self):
        return '`{}`'.format(str.__str__(self))

class hashtable(str):
    ...

class identifier(str):
    ...

class java_class(str):
    ...

class literal(str):
    def __str__(self):
        return "'{}'".format(str.__str__(self))

class long(int):
    def __str__(self):
        return '{}L'.format(int.__str__(self))

class object_expression(str):
    def __str__(self):
        return '[{}]'.format(str.__str__(self))

class scalar(str):
    ...

class string(str):
    def __str__(self):
        return '"{}"'.format(str.__str__(self))
    
# High level classes

@dataclass
class Arg(AST):
    name: str | expression | None
    value: expression

    def format(self):
        return (self.name + ' => ' if self.name else '') + _format_expression(self.value)
    
@dataclass
class Block(expression):
    body: list[command | flow_control]

    def format(self):
        body = [
            indention + 
            # Add indentions for nested blocks if needed
            _.format().replace(eol, eol + indention) +
            (';' + eol if isinstance(_, command) else '')
            for _ in self.body
        ]
        return '{' + eol + ''.join(body) + '}'
    
@dataclass
class KvPair(AST):
    name: expression
    value: expression

    def format(self):
        return self.name + ' => ' + self.value
    
@dataclass
class Script(AST):
    body: list[flow_control | command]

    def format(self):
        body = [_.format() + (';' if isinstance(_, command) else '') for _ in self.body if _]
        return eol.join(body)
    
# Commands

@dataclass
class Assert(command):
    test: expression
    message: expression | None

    def format(self):
        return 'assert {}{}'.format(self.test, ' : ' + self.message.format() if self.message else '')
    
@dataclass
class Break(command):
    def format(self):
        return 'break'

@dataclass
class Callcc(command):
    closure: AST

    def format(self):
        return 'callcc {}'.format(self.closure.format())

@dataclass
class Continue(command):
    def format(self):
        return 'continue'

@dataclass
class Done(command):
    def format(self):
        return 'done'

@dataclass
class Halt(command):
    def format(self):
        return 'halt'

@dataclass
class Import(command):
    target: str

    def format(self):
        return 'import {}'.format(self.target.format())

@dataclass
class ImportFrom(command):
    target: str
    path: str

    def format(self):
        return 'import {} from {}'.format(self.target.format(), self.path.format())

@dataclass
class Return(command):
    value: expression | None

    def format(self):
        return 'return{}'.format(' ' + self.value.format() if self.value else '')
    
@dataclass
class Throw(command):
    value: expression

    def format(self):
        return 'throw {}'.format(self.value.format())

@dataclass
class Yield(command):
    value: expression | None

    def format(self):
        return 'yield{}'.format(' ' + self.value.format() if self.value else '')

# Flow control

@dataclass
class Catch(flow_control):
    value: object
    body: Block
    
    def format(self):
        return 'catch {} {}'.format(self.value.format(), self.body.format())

@dataclass
class EnvBridge(flow_control):
    keyword: str
    identifier: str
    string: str | None
    body: Block
    
    def format(self):
        return '{} {}{} {}'.format(self.keyword, self.identifier, (self.string if self.string else ''), self.body.format())

@dataclass
class For(flow_control):
    initializer: list[expression]
    test: expression
    increment: list[expression]
    body: Block

    def format(self):
        test = self.test.format()
        if test:
            test = ' ' + test
        increment = ', '.join(_.format() for _ in self.increment)
        if increment:
            increment = ' ' + increment
        return 'for ({};{};{}) {}'.format(', '.join(_.format() for _ in self.initializer), test, increment, self.body.format())
    
@dataclass
class Foreach(flow_control):
    index: str | None
    value: str
    generator: expression
    body: Block

    def format(self):
        return 'foreach {}{} ({}) {}'.format((self.index + ' => ' if self.index else ''), self.value, self.generator.format(), self.body.format())

@dataclass
class If(flow_control):
    test: expression
    body: Block
    orelse: If | Block | None

    def format(self):
        return 'if ({}) {}{}'.format(self.test, self.body.format(), eol + 'else ' + self.orelse.format() if self.orelse else '')
    
@dataclass
class Try(flow_control):
    body: Block
    handler: exception_handler

    def format(self):
        return 'try {}{}{}'.format(self.body.format(), eol, self.handler.format())
    
@dataclass
class While(flow_control):
    test: expression
    body: Block

    def format(self):
        return 'while ({}) {}'.format(self.test.format(), self.body.format())
    
# Expressions

@dataclass
class Call(expression):
    function: str
    args: list[Arg]

    def format(self):
        return '{}({})'.format(self.function, ', '.join([_.format() for _ in self.args]))
    
@dataclass
class BinOp(expression):
    left: expression
    op: str
    right: expression

    def format(self):
        return '{} {} {}'.format(_format_expression(self.left), self.op, _format_expression(self.right))
    
@dataclass
class Index(expression):
    container: expression
    element: expression

    def format(self):
        return '{}[{}]'.format(_format_expression(self.container), _format_expression(self.element))
    
@dataclass
class UnaryOp(expression):
    op: str
    operand: expression

    def format(self):
        expression = _format_expression(self.operand)
        return self.op + expression if self.op not in ['++', '--'] else expression + self.op