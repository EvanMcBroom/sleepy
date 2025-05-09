#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import ply
from sleepy import *
import unittest

# These are scripts that should raise a lexer or parser error
# Determined by greping for and 'checkError', 'Error:', and 'YourCodeSucks'
# Each bug was then manually checked to see if it was a parser or runtime issue
illformedScripts = [
    'argerr.sl',
    'errors1.sl',
    'errors2.sl',
    'errors3.sl',
    'errors5.sl',
    'hoeserror.sl',
    'keyvalueerr.sl',
    'noterm.sl',
    'noterm2.sl',
    'scalref.sl',
    'sillysyntax.sl',
    # The real sleep code catches this as a runtime error due to '*8' not being a defined operator
    # Sleepy does not support operator bridges because it will cause unexpected precedence issues 
    # It this should actually be caught as a syntax error
    'warn.sl',
    # Skipped because sleepy doesn't parse literals
    # 'errors4.sl',
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

class TestCase1Lexer(unittest.TestCase):
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

class TestCase2Parser(unittest.TestCase):
    def test_corpus(self):
        for path, content in corpus('*.sl'):
            if path.split(os.sep)[-1] in illformedScripts:
                continue
            parser = SleepParser(debug=True, failfast=True)
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

class TestCase3Ast(unittest.TestCase):
    def __token_stream(self, content):
        lexer = SleepLexer()
        lexer.input(content)
        return [_ for _ in lexer.token_stream]

    def test_formatting(self):
        for path, content in corpus('*.sl'):
            if path.split(os.sep)[-1] in illformedScripts:
                continue
            # Get the original token stream
            tokenList1 = self.__token_stream(content)
            # Parse the script and format the AST
            ast = SleepParser(failfast=True).parse(content, tracking=True)
            formattedContent = format(ast)
            # Get the new token stream
            tokenList2 = self.__token_stream(formattedContent)
            # Check that they're the same
            self.assertEqual(len(tokenList1), len(tokenList2))
            for token1, token2 in zip(tokenList1, tokenList2):
                self.assertEqual(token1.type, token2.type)
                self.assertEqual(token1.value, token2.value)
 
if __name__ == '__main__':
    unittest.main()