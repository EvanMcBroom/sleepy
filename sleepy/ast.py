# -*- coding: utf-8 -*-

from __future__ import annotations

import itertools
import re
import typing
from dataclasses import dataclass
from sleepy.lexer import t_LITERAL, t_STRING

_literalRegex = re.compile(t_LITERAL.__doc__)
_stringRegex = re.compile(t_STRING.__doc__)

# Formatting options
eol = '\n'
indention = '    '

# Base classes

class Ast:
    start_lineno: int
    comment: str | None # Inline comment

class FlowControl(Ast):
    ...

class Command(Ast):
    ...

class Expression(Command):
    parenthesized: bool = False

    def __str__(self):
        return self.parenthesize(str.__str__(self))
    
    def parenthesize(self, value: str):
        return '({})'.format(value) if self.parenthesized else value

# High level classes

@dataclass
class Arg(Ast):
    name: str | int | Expression | None
    value: Expression | None
    trailing_sep: bool = False

    def __str__(self):
        trailing_sep = ',' if self.trailing_sep else ''
        return self.name if self.value == None else (str(self.name) + ' => ' if self.name != None else '') + str(self.value) + trailing_sep
    
# Values

@dataclass
class Boolean(Ast):
    value: bool

    def __str__(self):
        return 'true' if self.value else 'false'

@dataclass
class Null(Ast):
    def __str__(self):
        return '$null'
     
@dataclass
class Long(Ast):
    value: int

    def __str__(self):
        return str(self.value) + 'L'
    
# Single line comment
@dataclass
class Comment(Ast):
    message: str

    def __str__(self):
        return '# ' + self.message
    
@dataclass
class KvPair(Ast):
    name: Expression
    value: Expression

    def __str__(self):
        return self.name + ' => ' + self.value
    
@dataclass
class LineBreak(Ast):
    count: int

    def __str__(self):
        return ''

@dataclass
class LvalueTuple(Ast):
    values: tuple

    def __str__(self):
        return '({})'.format(', '.join(_ for _ in self.values))
      
@dataclass
class Script(Ast):
    body: list[FlowControl | Command]

    def __str__(self):
        body = [str(_) + (';' if isinstance(_, Command) else '') for _ in self.body if _]
        return eol.join(body)
    
    __calls = list()
    def __find_calls(self, node):
        if isinstance(node, Call):
            self.__calls.append(node.function)
        return node


    def __is_cyclic(self, xrefs, function, visited=set()):
        if function in visited:
            return True
        if function not in xrefs:
            return False
        for neighbour in xrefs[function]:
            if self.__is_cyclic(xrefs, neighbour, visited | {function}):
                return True
        return False
    
    # Returns an Ast for a specified function.
    def function(self, name, useCache=True):
        self.functions(useCache)
        matches = [_ for _ in Script.functions.data if _.identifier == name]
        return matches[0] if len(matches) > 0 else None
    
    # Returns the list of aliases and subroutines (e.g., functions) in a script.
    def functions(self, useCache=True):
        if not useCache or not hasattr(Script.functions, "data"):
            Script.functions.data = list()
            for statement in self.body:
                if isinstance(statement, EnvBridge) and statement.keyword in ['alias', 'sub']:
                    Script.functions.data.append(statement)
            Script.functions.data.sort(key=lambda statement: statement.identifier)
        return [_.identifier for _ in Script.functions.data]

    # A simple path tracing BFS algorithm slightly modified from qiao's solution.
    # The algorithm requires that there are no cycles in the call tree for the
    # script (e.g., the script does not have any recursive functions).
    # https://stackoverflow.com/a/8922151/11039217
    def paths(self, start, end, onlyFirst=False, useCache=True):
        xrefs = self.xrefs(useCache)
        if any([self.__is_cyclic(self.xrefs(useCache), _) for _ in self.functions(useCache)]):
            raise RecursionError("Path tracing is not supported for scripts with recursive functions.")
        paths = []
        queue = []
        queue.append([start])
        while queue:
            # get the first path from the queue
            path = queue.pop(0)
            # get the lAst node from the path
            node = path[-1]
            # path found
            if node == end:
                if onlyFirst:
                    return path
                else:
                    paths.append(path)
            # enumerate all adjacent nodes, construct a 
            # new path and push it into the queue
            for adjacent in xrefs.get(node, []):
                new_path = list(path)
                new_path.append(adjacent)
                queue.append(new_path)
        return paths 
    
    # Returns the cross-references for the main script and all functions it defines.
    def xrefs(self, useCache=True):
        if not useCache or not hasattr(Script.xrefs, "data"):
            Script.xrefs.data = {_: list() for _ in self.functions()}
            # An empty string is used to reference the main script
            # This is used rather than None to allow the dict to be
            # easily sorted.
            Script.xrefs.data[''] = list()
            for statement in self.body:
                self.__calls = list()
                walk(statement, self.__find_calls)
                self.__calls = list(set(self.__calls))
                key = ''
                if isinstance(statement, EnvBridge) and statement.keyword in ['alias', 'sub'] and statement.identifier in Script.xrefs.data:
                    key = statement.identifier
                Script.xrefs.data[key] = sorted(list(set(Script.xrefs.data[key] + self.__calls)))
        return Script.xrefs.data

# Commands

@dataclass
class Assert(Command):
    test: Expression
    message: string | None

    def __str__(self):
        return 'assert {}{}'.format(self.test, ' : ' + str(self.message) if self.message != None else '')
    
@dataclass
class Break(Command):
    def __str__(self):
        return 'break'

@dataclass
class Callcc(Command):
    closure: Ast

    def __str__(self):
        return 'callcc {}'.format(self.closure)

@dataclass
class Continue(Command):
    def __str__(self):
        return 'continue'

@dataclass
class Done(Command):
    def __str__(self):
        return 'done'

@dataclass
class Halt(Command):
    def __str__(self):
        return 'halt'

@dataclass
class Import(Command):
    target: str
    path: str | None

    def __str__(self):
        return 'import {}{}'.format(self.target, ' from: {}'.format(self.path) if self.path != None else '')

@dataclass
class Nop(Command):
    def __str__(self):
        return ''
    
@dataclass
class Return(Command):
    value: Expression | object | None

    def __str__(self):
        return 'return{}'.format(' ' + str(self.value) if self.value != None else '')
    
@dataclass
class Throw(Command):
    value: Expression

    def __str__(self):
        return 'throw {}'.format(self.value)

@dataclass
class Yield(Command):
    value: Expression | None

    def __str__(self):
        return 'yield{}'.format(' ' + str(self.value) if self.value != None else '')

# Flow control

@dataclass
class AssignLoop(FlowControl):
    value: str
    generator: Expression
    body: Block

    def __str__(self):
        return 'while {} ({}) {}'.format(self.value, self.generator, self.body)
    
@dataclass
class EnvBridge(FlowControl):
    keyword: str
    identifier: str
    string: str | None
    body: Block
    
    def __str__(self):
        return '{} {}{} {}'.format(self.keyword, self.identifier, (self.string if self.string != None else ''), self.body)

@dataclass
class For(FlowControl):
    initializer: list[Expression]
    test: Expression
    increment: list[Expression]
    body: Block

    def __str__(self):
        test = str(self.test)
        if test:
            test = ' ' + test
        increment = ', '.join(str(_) for _ in self.increment)
        if increment:
            increment = ' ' + increment
        return 'for ({};{};{}) {}'.format(', '.join(str(_) for _ in self.initializer), test, increment, self.body)
    
@dataclass
class Foreach(FlowControl):
    index: str | None
    value: str
    generator: Expression
    body: Block

    def __str__(self):
        return 'foreach {}{} ({}) {}'.format((self.index + ' => ' if self.index else ''), self.value, self.generator, self.body)

@dataclass
class If(FlowControl):
    test: Expression
    body: Block
    orelse: If | Block | None

    def __str__(self):
        return 'if ({}) {}{}'.format(self.test, self.body, (eol + 'else ' + str(self.orelse)) if self.orelse else '')
    
@dataclass
class TryCatch(FlowControl):
    body: Block
    value: object
    handler: Block

    def __str__(self):
        return 'try {}{}catch {} {}'.format(self.body, eol, self.value, self.handler)
     
@dataclass
class While(FlowControl):
    test: Expression
    body: Block

    def __str__(self):
        return 'while ({}) {}'.format(self.test, self.body)


# Values

class Address(Expression, str):
    ...

class Array(Expression, str):
    ...

class BacktickExpr(Expression, str):
    def __str__(self):
        return self.parenthesize('`{}`'.format(str.__str__(self)))

class ClassLiteral(Expression, str):
    ...

class HashTable(Expression, str):
    ...

class Identifier(Expression, str):
    ...

class Literal(Expression, str):
    def __str__(self):
        return self.parenthesize("'{}'".format(str.__str__(self)))
    
class Scalar(Expression, str):
    ...

class String(Expression, str):
    def __str__(self):
        return self.parenthesize('"{}"'.format(str.__str__(self)))
     
# Expressions

@dataclass
class Block(Expression):
    body: list[Command | FlowControl]

    def __str__(self):
        body = []
        for statement in self.body:
            formattedStatement = str(statement)
            # Identify multiline literals and strings with embedded newlines
            # These need to be gathered because they should not be indented
            embeddedNewlines = [_ for _ in _literalRegex.finditer(formattedStatement) if eol in _.string]
            embeddedNewlines += [_ for _ in _stringRegex.finditer(formattedStatement) if eol in _.string]
            # Gather the indexes from the start of the original string of each embedded newline
            embeddedNewlines = [
                # Start of a multiline literal or string
                result.span()[0] +
                # Index of the embedded newline within it
                _.span()[0]
                for result in embeddedNewlines
                    for _ in re.finditer(eol, result.group())
            ]
            # Build the final indented statement
            # Approach built with help from: https://stackoverflow.com/a/28829204
            indentedStatement = ''
            for key, group in itertools.groupby(enumerate(formattedStatement), lambda _: not _[1] == eol):
                if key:
                    # Concatenate non-newlines to the final formatted statement without modifications
                    indentedStatement += ''.join([char for _, char in group])
                else:
                    # For newlines, identify if its an embedded newline
                    startingIndex, _ = next(group)
                    eolCount = 1 + len(list(group))
                    indentedStatement += (eol + indention if startingIndex not in embeddedNewlines else eol) * eolCount
            # Add the statement to the body of the block
            # Indent the first line which has not been done yet
            body += [
                indention + indentedStatement +
                (';' if isinstance(statement, Command) else '') + eol
            ]
        return self.parenthesize('{' + eol + ''.join(body) + '}')
    
@dataclass
class Call(Expression):
    function: str
    args: list[Arg]

    def __str__(self):
        return self.parenthesize('{}({})'.format(self.function, ', '.join([str(_) for _ in self.args])))
    
@dataclass
class BinOp(Expression):
    left: Expression
    op: str
    right: Expression
    negate: bool = False

    def __str__(self):
        return self.parenthesize('{} {}{} {}'.format(self.left, '!' if self.negate else '', self.op, self.right))
    
@dataclass
class Index(Expression):
    container: Expression
    element: Expression

    def __str__(self):
        return self.parenthesize('{}[{}]'.format(self.container, self.element))

@dataclass
class ObjExpr(Expression):
    target: Expression
    message: str | None
    args: list[Arg] | None

    def __str__(self):
        return '[{}'.format(self.target) + \
            (' {}'.format(self.message) if self.message else '') + \
            (': {}'.format(', '.join(str(_) for _ in self.args)) if self.args else '') + \
            ']'

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

    def __str__(self):
        # Adding a space for predicate bridges
        op = self.op + (' ' if len(self.op) > 1 and self.op[0] == '-' and self.op[1] != '-' else '')
        return self.parenthesize(op + str(self.operand) if op not in ['++', '--'] else str(self.operand) + op)

# Functions

def format(node: Ast):
    return str(node)

def walk(node, visitor=None):
    if type(node) == Arg:
        node.name = walk(node.name, visitor)
        node.value = walk(node.value, visitor)
    elif type(node) == Assert:
        node.test = walk(node.test, visitor)
    elif type(node) == AssignLoop:
        node.value = walk(node.value, visitor)
        node.body = walk(node.body, visitor)
    elif type(node) == BinOp:
        node.left = walk(node.left, visitor)
        node.right = walk(node.right, visitor)
    elif type(node) == Block:
        node.body = list(walk(_, visitor) for _ in node.body)
    elif type(node) == Call:
        node.args = list(walk(_, visitor) for _ in node.args)
    elif type(node) == Callcc:
        node.closure = walk(node.closure, visitor)
    elif type(node) == EnvBridge:
        node.body = walk(node.body, visitor)
    elif type(node) == For:
        node.initializer = list(walk(_, visitor) for _ in node.initializer)
        node.increment = list(walk(_, visitor) for _ in node.increment)
    elif type(node) == Foreach:
        node.generator = walk(node.generator, visitor)
        node.body = walk(node.body, visitor)
    elif type(node) == If:
        node.test = walk(node.test, visitor)
        node.body = walk(node.body, visitor)
        node.orelse = walk(node.orelse, visitor)
    elif type(node) == Index:
        node.container = walk(node.container, visitor)
    elif type(node) == KvPair:
        node.name = walk(node.name, visitor)
        node.value = walk(node.value, visitor)
    elif type(node) == LvalueTuple:
        node.values = tuple(walk(_, visitor) for _ in node.values)
    elif type(node) == ObjExpr:
        node.message = walk(node.message, visitor)
        node.target = walk(node.target, visitor)
        node.args = list(walk(_, visitor) for _ in node.args)
    elif type(node) == Return:
        node.value = walk(node.value, visitor)
    elif type(node) == Script:
        node.body = list(walk(_, visitor) for _ in node.body)
    elif type(node) == Throw:
        node.value = walk(node.value, visitor)
    elif type(node) == TryCatch:
        node.body = walk(node.body, visitor)
        node.value = walk(node.value, visitor)
        node.handler = walk(node.handler, visitor)
    elif type(node) == While:
        node.test = walk(node.test, visitor)
        node.body = walk(node.body, visitor)
    elif type(node) == Yield:
        node.value = walk(node.value, visitor)
    elif type(node) == UnaryOp:
        node.operand = walk(node.operand, visitor)
    return visitor(node) if visitor else node