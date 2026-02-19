# -*- coding: utf-8 -*-
# Repairs the following script issues which are not allowed by sleepy
# but are allowed by the parser in the official Sleep distribution:
# - Adds missing semicolons before a script block's close (e.g '}')

import sys
from sleepy.lexer import *

if len(sys.argv) > 1:
    path = sys.argv[1]
    with open(path, 'r') as file:
        print(preprocess(file.read(), repair_missing_semicolons=True))
else:
    print('{} <path>'.format(sys.argv[0]))