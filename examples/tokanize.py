import sys
from sleepy.parser import *

if len(sys.argv) > 1:
    path = sys.argv[1]
    with open(path, 'r') as file:
        lexer = SleepLexer()
        lexer.input(file.read())
        for token in lexer:
            print(token)
else:
    print('{} <path>'.format(sys.argv[0]))