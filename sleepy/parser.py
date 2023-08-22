# -*- coding: utf-8 -*-

import os
from ply import *
from sleepy.ast import *
from sleepy.lexer import *

failfast = False
parser = None
quiet = False

# Tokens are ordered from lowest to highest precedence
# Using the C++ and Python precedence rules
# https://en.cppreference.com/w/cpp/language/operator_precedence
# https://docs.python.org/3/reference/expressions.html#operator-precedence
precedence = (
    ('left', 'BINARY_PREDICATE_BRIDGE'),
    ('right', 'UNARY_PREDICATE_BRIDGE'),
    ('right', '=', 'ANDEQUAL', 'CATEQUAL', 'DIVEQUAL', 'EXPEQUAL', 'LSHIFTEQUAL', 'MINUSEQUAL', 'OREQUAL', 'PLUSEQUAL', 'RSHIFTEQUAL', 'TIMESEQUAL', 'XOREQUAL'),
    ('left', 'LOR'),
    ('left', 'LAND'),
    ('left', '|'),
    ('left', '^'),
    ('left', '&'),
    ('left', 'EQ', 'NE', 'EQI', 'NEQI', 'SPACESHIP'),
    ('left', '<', '>', 'LE', 'GE'),
    ('left', 'LSHIFT', 'RSHIFT'),
    ('left', '+', '-', '.'),
    ('left', '*', '/', '%', 'x'),
    ('right', 'UNARY_PLUS', 'UNARY_MINUS', 'LNOT', '!'),
    ('left', 'INC', 'DEC'),
    ('left', 'EXP'),
)

def p_empty(p):
    ''' empty : '''
    pass

# An ID is only a valid rvalue when it is a previously defined
# named parameter in a function call. Example:
# - f(a => 1, a + 2 => 3)
# If the ID is used correctly should be checked at runtime
def p_rvalue(p):
    ''' rvalue : address
               | backtick_expr
               | block
               | function_call
               | identifier
               | java_class
               | literal
               | lvalue
               | object_expr
               | string
               | DOUBLE
               | FALSE
               | LONG
               | NULL
               | NUMBER
               | TRUE
    '''
    p[0] = p[1]

def p_lvalue(p):
    ''' lvalue : array
               | hashtable
               | scalar
    '''
    p[0] = p[1]

def p_assignment_operator(p):
    ''' assignment_operator : '='
                            | ANDEQUAL
                            | CATEQUAL
                            | DIVEQUAL
                            | EXPEQUAL
                            | LSHIFTEQUAL
                            | MINUSEQUAL
                            | OREQUAL
                            | PLUSEQUAL
                            | RSHIFTEQUAL
                            | TIMESEQUAL
                            | XOREQUAL
    '''
    p[0] = p[1]

def p_address(p):
    ''' address : ADDRESS
    '''
    p[0] = address(p[1])

def p_array(p):
    ''' array : '@' ID
    '''
    p[0] = array(p[1] + p[2])


def p_backtick_expr(p):
    ''' backtick_expr : BACKTICK_EXPR
    '''
    p[0] = backtick_expression(p[1])

def p_hashtable(p):
    ''' hashtable : '%' ID
    '''
    p[0] = hashtable(p[1] + p[2])

def p_identifier(p):
    ''' identifier : ID
    '''
    p[0] = identifier(p[1])

def p_java_class(p):
    ''' java_class : JAVA_CLASS
    '''
    p[0] = java_class(p[1])

def p_literal(p):
    ''' literal : LITERAL
    '''
    p[0] = literal(p[1])

def p_object_expr(p):
    ''' object_expr : OBJECT_EXPR
    '''
    p[0] = object_expression(p[1])

def p_scalar(p):
    ''' scalar : SCALAR
    '''
    p[0] = scalar(p[1])

def p_string(p):
    ''' string : STRING
    '''
    p[0] = string(p[1])

def p_expression_binary(p):
    ''' expression : expression '-' expression
                   | expression '.' expression
                   | expression '*' expression
                   | expression '/' expression
                   | expression '&' expression
                   | expression '%' expression
                   | expression '^' expression
                   | expression '+' expression
                   | expression '<' expression
                   | expression '=' expression
                   | expression '>' expression
                   | expression '|' expression
                   | expression 'x' expression
                   | expression ANDEQUAL expression
                   | expression CATEQUAL expression
                   | expression DIVEQUAL expression
                   | expression EQ expression
                   | expression EQI expression
                   | expression EXP expression
                   | expression EXPEQUAL expression
                   | expression GE expression
                   | expression LAND expression
                   | expression LE expression
                   | expression LOR expression
                   | expression LSHIFT expression
                   | expression LSHIFTEQUAL expression
                   | expression MINUSEQUAL expression
                   | expression NE expression
                   | expression NEQI expression
                   | expression OREQUAL expression
                   | expression PLUSEQUAL expression
                   | expression RSHIFT expression
                   | expression RSHIFTEQUAL expression
                   | expression SPACESHIP expression
                   | expression TIMESEQUAL expression
                   | expression XOREQUAL expression
                   | expression ID expression %prec BINARY_PREDICATE_BRIDGE
                   | expression '!' ID expression %prec BINARY_PREDICATE_BRIDGE
                   | '(' expression ')'
                   | rvalue
    '''
    if len(p) == 5:
        p[0] = UnaryOp(
            op=p[2],
            operand=BinOp(
                left=p[1],
                op=p[3],
                right=p[4]
            )
        )
    elif len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = BinOp(
                left=p[1],
                op=p[2],
                right=p[3],
            )
    else:
        p[0] = p[1]

def p_expression_index(p):
    ''' expression : expression '[' expression ']'
    '''
    p[0] = Index(
        container=p[1],
        element=p[3]
    )

def p_expression_unary_prefix(p):
    ''' expression : '+' expression %prec UNARY_PLUS
                   | '-' expression %prec UNARY_MINUS
                   | '!' expression %prec LNOT
                   | UNARY_PREDICATE_BRIDGE expression
    '''
    p[0] = UnaryOp(
        op=p[1],
        operand=p[2]
    )

def p_expression_unary_postfix(p):
    ''' expression : expression INC
                   | expression DEC
    '''
    p[0] = UnaryOp(
        op=p[2],
        operand=p[1]
    )

def p_args(p):
    ''' args : args ',' expression
             | args ',' arg_passed_by_name
             | args ',' key_value_pair
             | args ','
             | expression
             | arg_passed_by_name
             | key_value_pair
             | empty
    '''
    arg = p[len(p) - 1]
    if arg == ',':
        p[0] = p[1]
    else:
        if isinstance(arg, KvPair):
            arg = Arg(
                name=arg.name,
                value=arg.value,
            )
        elif not isinstance(arg, Arg):
            arg = Arg(
                name=None,
                value=arg,
            )
        if len(p) == 4:
            p[0] = p[1] + [arg]
        else: # len(p) == 2
            p[0] = [arg]

# args should be seperated by a comma but sleep allows for space seperators
def p_args_error(p):
    ''' args : args error expression
             | args error arg_passed_by_name
             | args error key_value_pair
    '''
    if failfast:
        raise SyntaxError(str(p))
    if not quiet:
        print('- Did you forget to add a comma?')
    p_args(p)

def p_arg_passed_by_name(p):
    ''' arg_passed_by_name : ARG_PASSED_BY_NAME
    '''
    p[0] = Arg(
        name=p[1][1:],
        value=p[1][1:]
    )

# Normally, this should only be defined as ID ARROW rvalue
# expression ARROW rvalue is used instead because expression includes ID
# According to the docs, %() should only take IDs for keys
# %() is actually treated by the unit tests as a normal function though (ex. closurekvp.sl)
# So it's keys should take lvalues and numbers as well
# Also, some unit tests use the result of expressions as keys (ex. multi.sl)
# So it should take full expressions in addition to IDs, which will include lvalues and NUMBERs
def p_key_value_pair(p):
    ''' key_value_pair : expression ARROW expression
    '''
    p[0] = KvPair(
        name=p[1],
        value=p[3]
    )

def p_comment(p):
    ''' comment : COMMENT
    '''
    p[0] = ('comment', p[1][1:].rstrip())

def p_script(p):
    ''' script : script statement
               | statement
               | EOF
    '''
    if len(p) == 3:
        p[0] = Script(
            body=p[1].body + [p[2]]
        )
    else:
        p[0] = Script(
            body=[p[1]]
        )

def p_block(p):
    ''' block : '{' script '}'
              | '{' '}'
    '''
    if len(p) == 4:
        p[0] = Block(
            body=p[2].body
        )
    else:
        p[0] = Block(
            body=[]
        )

def p_statement(p):
    ''' statement : command ';'
                  | comment
                  | flow_control
    '''
    p[0] = p[1]

# Statements should be seperated by a comma as 
# The official sleep parser allows for space seperators but we'll flag it
def p_statement_error(p):
    ''' statement : error
    '''
    global parser
    parser.errok()
    if failfast:
        raise SyntaxError(str(p))
    if not quiet:
        print('- Did you forget to add a semicolon?')
    return p

def p_command(p):
    ''' command : assertion
                | BREAK
                | callcc
                | CONTINUE
                | DONE
                | expression
                | HALT
                | import
                | tuple_assignment
                | return
                | throw
                | yield
                | empty
    '''
    p[0] = p[1]

def p_assertion(p):
    ''' assertion : ASSERT expression
                  | ASSERT expression ':' STRING
    '''
    if len(p) == 3:
        p[0] = Assert(
            test=p[2],
            message=None
        )
    else:
        p[0] = Assert(
            test=p[2],
            message=p[4]
        )

def p_callcc(p):    
    ''' callcc : CALLCC rvalue
    '''
    p[0] = Callcc(
        closure=p[2]
    )

def p_function_call(p):
    '''function_call : ID '(' args ')'
                     | '%' '(' args ')'
                     | '@' '(' args ')'
    '''
    p[0] = Call(
        function=p[1],
        args=p[3],
    )

def p_import(p):
    ''' import : IMPORT import_target import_suffix
    '''
    suffix = p[3]
    if suffix:
        p[0] = ImportFrom(
            target=p[2],
            path=suffix
        )
    else:     
        p[0] = Import(
            target=p[2]
        )

def p_import_target(p):
    ''' import_target : import_target '.' ID
                      | import_target '.' '*'
                      | ID
    '''
    if len(p) > 2:
        p[0] =  p[1] + p[2] + p[3]
    else:
        p[0] = p[1]

def p_import_suffix(p):
    ''' import_suffix : FROM ':' IMPORT_PATH
                      | FROM ':' STRING
                      | empty
    '''
    if len(p) == 4:
        p[0] = p[3]

def p_lvalues(p):
    ''' lvalues : lvalues ',' lvalue
                | lvalues ','
                | lvalue
    '''
    if len(p) == 4: # lvalues ',' lvalue
        p[0] = p[1] + [p[3]]
    elif len(p) == 3: # lvalues ','
        p[0] = p[1]
    else: # lvalue
        p[0] = [p[1]]

# lvalues should be seperated by a comma as 
# The official sleep parser allows for space seperators but we'll flag it
def p_lvalues_error(p):
    ''' lvalues : lvalues error lvalue
    '''
    if failfast:
        raise SyntaxError(str(p))
    if not quiet:
        print('- Did you forget to add a comma?')
    p[0] = p[1] + [p[3]]

def p_lvalue_tuple(p):
    ''' lvalue_tuple : '(' lvalues ')'
    '''
    if type(p[2]) == list:
        p[0] = tuple(p[2])
    else:
        p[0] = p[2]

def p_tuple_assignment(p):
    ''' tuple_assignment : lvalue_tuple assignment_operator expression
    '''
    p[0] = BinOp(
        left=p[1],
        op=p[2],
        right=p[3]
    )

def p_return(p):
    ''' return : RETURN expression
               | RETURN
    '''
    value = None if len(p) == 2 else p[2]
    p[0] = Return(
        value=value
    )

def p_throw(p):
    ''' throw : THROW expression
    '''
    p[0] = Throw(
        value=p[2]
    )

def p_flow_control(p):
    ''' flow_control : assignment_loop
                     | conditional
                     | environment_bridge
                     | for_loop
                     | foreach
                     | trycatch
                     | while_loop
    '''
    p[0] = p[1]

def p_assignment_loop(p):
    ''' assignment_loop : WHILE SCALAR '(' expression ')' block
    '''
    p[0] = Foreach(
        index=None,
        value=p[2],
        generator=p[4],
        body=p[6]
    )

def p_conditional(p):
    ''' conditional : IF '(' expression ')' block else
    '''
    p[0] = If(
        test=p[3],
        body=p[5],
        orelse=p[6]
    )

def p_conditional_else(p):
    ''' else : ELSE conditional
             | ELSE block
             | empty
    '''
    if len(p) == 3:
        if isinstance(p[2], If):
            p[0] = [p[2]]
        else: # ELSE block
            p[0] = p[2]
    else: # empty
        p[0] = []

# Docs: 9.3 "Extend Sleep"
# The "predicate" variant of a sleep bridge is currently not supported
# because it'd cause an ambigious grammar with the function_call rule
# Example: keyword (predicate) { commands; }
def p_environment_bridge(p):
    ''' environment_bridge : ID ID block
                           | ID ID STRING block
    '''
    if len(p) == 4:
        p[0] = EnvBridge(
            keyword=p[1],
            identifier=p[2],
            string=None,
            body=p[3]
        )
    else: # ID ID STRING block
        p[0] = EnvBridge(
            keyword=p[1],
            identifier=p[2],
            string=p[3],
            body=p[4]
        )

def p_for_loop(p):
    ''' for_loop : FOR '(' for_loop_initializer ';' expression ';' for_loop_increment ')' block
    '''
    p[0] = For(
        initializer=p[3],
        test=p[5],
        increment=p[7],
        body=p[9]
    )

def p_for_loop_initializer(p):
    ''' for_loop_initializer : for_loop_initializer ',' expression
                             | for_loop_initializer ','
                             | expression
                             | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        if p[1]:
            p[0] = [p[1]]
        else: # empty
            p[0] = []
            
def p_for_loop_increment(p):
    ''' for_loop_increment : for_loop_initializer
    '''
    p[0] = p[1]

def p_foreach(p):
    ''' foreach : FOREACH SCALAR ARROW SCALAR '(' foreach_generator ')' block
                | FOREACH SCALAR '(' foreach_generator ')' block
    '''
    if len(p) == 9:
        p[0] = Foreach(
            index=p[2],
            value=p[4],
            generator=p[6],
            body=p[8]
        )
    else:
        p[0] = Foreach(
            index=None,
            value=p[2],
            generator=p[4],
            body=p[6]
        )

def p_foreach_generator(p):
    ''' foreach_generator : expression
    '''
    p[0] = p[1]

def p_trycatch(p):
    ''' trycatch : TRY block CATCH SCALAR block
    '''
    p[0] = Try(
        body=p[2],
        handler=Catch(
            value=p[4],
            body=p[5]
        )
    )

def p_while_loop(p):
    ''' while_loop : WHILE '(' expression ')' block
    '''
    p[0] = While(
        test=p[3],
        body=p[5]
    )

def p_yield(p):
    ''' yield : YIELD
              | YIELD expression
    '''
    value = None if len(p) == 2 else p[2]
    p[0] = Yield(
        value=value
    )

# Error formatting
class SyntaxError(Exception):
    pass

def p_error(p):
    if failfast:
        raise SyntaxError(str(p))
    if not quiet:
        if p:
            print('Syntax error at line {}: {}'.format(p.lineno,str(p)))
        else:
            print("Syntax error at EOF")

class SleepParser(object):
    def __init__(self, **kwargs):
        global failfast, parser, quiet
        failfast = kwargs.get('failfast', False)
        quiet = kwargs.get('quiet', False)
        self.debug = kwargs.get('debug', False)
        self.lexer = kwargs.get('lexer', SleepLexer())
        parser = yacc.yacc(start="script", debug=self.debug)

    def parse(self, code, tracking=False):
        global parser
        return parser.parse(code, tracking=tracking)