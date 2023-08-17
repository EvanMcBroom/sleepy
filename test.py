#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import ply
import unittest
from sleepy import *

# These are scripts that should raise a lexer or parser error
# Determined by greping for and 'checkError', 'Error:', and 'YourCodeSucks'
# Each bug was then manually checked to see if it was a parser or runtime issue
illformedScripts = [
    'argerr.sl',
    'errors1.sl',
    'errors2.sl',
    'errors3.sl',
    'errors5.sl',
    'keyvalueerr.sl',
    'noterm.sl',
    'noterm2.sl',
    'scalref.sl',
    # The real sleep code catches this as a runtime error due to '*8' not being a defined operator
    # Sleepy does not support operator bridges because it will cause unexpected precedence issues 
    # It this should actually be caught as a syntax error
    'warn.sl',
    # Skipped because sleepy doesn't parse literals or object expressions
    # 'errors4.sl',
    # 'hoeserror.sl',
    # 'sillysyntax.sl'
]

runtimeErrorScripts = [
    # IDs that have not previously been used as a function parameter (e.g., barewords)
    # should be determined at runtime
    'bareword.sl',
    'clazz.sl',
    # Expressions should be determined at runtime if they evaluate to a string
    'concaterrs.sl',
    'debugce.sl',
    'imperror.sl',
    'imperror.sl',
    'impfrom3.sl',
    'include.sl',
    'squote.sl',
    'unicodeseq.sl'
]

def corpus(glob):
    for path in pathlib.Path('tests').glob(glob):
        with open(path, 'r') as file:
            yield (str(path), file.read())

class TestLexer(unittest.TestCase):
    def test_corpus(self):
        for path, content in corpus('*.sl'):
            if path.split(os.sep)[-1] in illformedScripts:
                continue
            lexer = SleepLexer()
            lexer.input(content)
            for token in lexer:
                self.assertIsInstance(token, ply.lex.LexToken)

    def test_error_handling(self):
        for script in illformedScripts:
            path, content = list(corpus(script))[0]
            lexer = SleepLexer()
            lexer.input(content)
            try:
                for token in lexer:
                    pass
            # Only catch illegal character exceptions
            # These are expected for the illformed scripts
            except IllegalCharacter:
                pass

class TestParser(unittest.TestCase):
    def test_corpus(self):
        for path, content in corpus('*.sl'):
            if path.split(os.sep)[-1] in illformedScripts:
                continue
            parser = SleepParser(debug=True)
            parser.parse(content, tracking=True)

    def test_error_handling(self):
        for script in illformedScripts:
            path, content = list(corpus(script))[0]
            try:
                parser = SleepParser(debug=True, failfast=True)
                parser.parse(content, tracking=True)
            # Only catch syntax error exceptions
            # These are expected for the illformed scripts
            except IllegalCharacter:
                pass
            except SyntaxError:
                pass
                
if __name__ == '__main__':
    unittest.main()