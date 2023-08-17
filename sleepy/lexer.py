# -*- coding: utf-8 -*-

import decimal
import fractions
from ply import *

debug = False

# Does not include any sleep extensions (e.g., 'bridges')
# Cobalt strike extends sleep to include:
# alias, bind, command, item, on, popup, report, set, ssh_alias
keywords = (
    'assert',
    'break',
    'callcc',
    'catch',
    'continue',
    'done',
    'else',
    'false',
    'for',
    'foreach',
    'from',
    'halt',
    'if',
    'import',
    'return',
    'throw',
    'true',
    'try',
    'while',
    'yield'
)

keywords = {keyword: keyword.upper() for keyword in keywords}

assignment_operators = (
    'ANDEQUAL',
    'CATEQUAL',
    'DIVEQUAL',
    'LSHIFTEQUAL',
    'MINUSEQUAL',
    'OREQUAL',
    'PLUSEQUAL',
    'RSHIFTEQUAL',
    'TIMESEQUAL',
    'XOREQUAL'
)

tokens = tuple(keywords.values()) + assignment_operators + (
    'ADDRESS',
    'ARG_PASSED_BY_NAME',
    'ARROW',
    'BACKTICK_EXPR',
    'COMMENT',
    'DEC',
    'DOUBLE',
    'EOF',
    'EQ',
    'EQI', # Equal identity
    'EXP',
    'EXPEQUAL',
    'GE',
    'ID',
    'IMPORT_PATH',
    'INC',
    'JAVA_CLASS',
    'LAND', # Logical and
    'LE',
    'LITERAL',
    'LONG',
    'LOR',
    'LSHIFT',
    'NE',
    'NEQI', # Not equal identity
    'NULL',
    'NUMBER',
    'OBJECT_EXPR',
    'RSHIFT',
    'SCALAR',
    'SPACESHIP',
    'STRING',
    'UNARY_PREDICATE_BRIDGE'
)

# These will be checked last
literals = "!.&@,/=%\\-+x*^|:;{\}[]()<>"

# Assignment operators
t_ANDEQUAL    = r'&='
t_CATEQUAL    = r'\.='
t_DIVEQUAL    = r'/='
t_EXPEQUAL    = r'\*\*='
t_LSHIFTEQUAL = r'<<='
t_MINUSEQUAL  = r'-='
t_OREQUAL     = r'\|='
t_PLUSEQUAL   = r'\+='
t_RSHIFTEQUAL = r'>>='
t_TIMESEQUAL  = r'\*='
t_XOREQUAL    = r'\^='

# Increment/decrement
t_INC = r'\+\+'
t_DEC = r'--'

# Bitewise operators
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'

# Logical operators
t_LAND = r'&&'
t_LOR  = r'\|\|'

# Arithmetic operators
t_EXP = r'\*\*='

# Match predicates before IDs
t_UNARY_PREDICATE_BRIDGE = r'-[a-zA-Z]+'

# Match import path before id
def t_IMPORT_PATH(t):
    r"(\w+/)+\w+\.\w+"
    t.value = t.value[1:-1]
    return t

# Matches IDs and keywords
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value,'ID')
    return t

t_ADDRESS            = r'\&[a-zA-Z_][a-zA-Z_0-9]*'
t_ARROW              = r'=>'
t_JAVA_CLASS         = r'\^([a-zA-Z_$][a-zA-Z\d_$]*\.)*[a-zA-Z_$][a-zA-Z\d_$]*'
t_ARG_PASSED_BY_NAME = r'\\(\@|\%|\$)[a-zA-Z_][a-zA-Z_0-9]*'
t_NULL               = r'\$null'
t_SCALAR             = r'(\$\w+|\$\+)'

# Comparisons
t_EQ        = r'=='
t_EQI       = r'=~'
t_LE        = r'<='
t_GE        = r'>='
t_NE        = r'!=(?![=~])'
t_NEQI      = r'!=~'
t_SPACESHIP = r'<=>'

def t_BACKTICK_EXPR(t):
    r"`([^\\\n]|(\\.))*?`"
    t.value = t.value[1:-1]
    return t

def t_DOUBLE(t):
    r'\d+\.\d+'
    t.value = fractions.Fraction(t.value)
    return t

def t_LITERAL(t):
    r"'([^\\']|(\\.))*([^\\']|(\\[^\\]))?'"
    t.value = t.value[1:-1]
    return t

def t_LONG(t):
    r'(0x[0-9a-fA-F]+|(?<!0x)\d+)L'
    t.value = t.value[:-1]
    return t_NUMBER(t)

def t_NUMBER(t):
    r'(0x[0-9a-fA-F]+|(?<!0x)\d+)'
    if len(t.value) > 2 and t.value[:2] == '0x':
        t.value = int(t.value, 16)
    elif t.value[0] == '0':
        t.value = int(t.value, 8)
    t.value = decimal.Decimal(t.value)
    return t

def t_STRING(t):
    r'"([^\\"]|(\\.))*([^\\"]|(\\[^\\]))?"'
    t.value = t.value[1:-1]
    t.lexer.lineno += t.value.count('\n')
    return t

# Define after LITERAL and STRING to not catch embedded values
def t_OBJECT_EXPR(t):
    r'(?<![a-zA-Z_0-9`)\]])\[(?:[^[\]]+|\[[^\]]+?\]|\n)+\]'
    t.value = t.value[1:-1]
    return t

# Ignored characters
t_ignore  = ' \t'

def t_ignore_COMMENT(t):
    r'\#.*\n'
    t.lexer.lineno += 1

# Don't generate newline tokens when inside of parenthesis, brackets, or braces
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

class IllegalCharacter(Exception):
    pass

# Error formatting
def t_error(t):
    raise IllegalCharacter(t.value[0])

def filter(lexer):
    token = None
    for token in iter(lexer.token, None):
        yield token
    lineno = 1
    if token is not None:
        lineno = token.lineno
    # Return an EOF token
    token = lex.LexToken()
    token.type = 'EOF'
    token.value = None
    token.lineno = lineno
    token.lexpos = 0
    yield token

class SleepLexer(object):
    def __init__(self, debug=0, reflags=0):
        self.lexer = lex.lex(debug=debug, reflags=reflags)
        self.token_stream = None

    def __iter__(self):
        return self

    def __next__(self): # Python 2: def next(self)
        token = self.token()
        if token:
            return token
        raise StopIteration

    def input(self, s, add_endmarker=True):
        self.lexer.paren_count = 0
        self.lexer.input(s)
        self.token_stream = filter(self.lexer)

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None