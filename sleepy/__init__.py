# -*- coding: utf-8 -*-

__version__ = '1.1'
__author__ = 'Evan McBroom'

# Replace Python's builtin re module to regex.
# The upgrade allows ply to use recursive regex expressions.
# Reference: https://github.com/mrabarnett/mrab-regex
import sys
del sys.modules['re']
sys.modules['re'] = __import__('regex')  

from .lexer import *
from .parser import *