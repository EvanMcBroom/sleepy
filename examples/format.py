# -*- coding: utf-8 -*-
# Formats a sleep script.

import sys
from sleepy.ast import format
from sleepy.parser import *

if len(sys.argv) > 1:
    path = sys.argv[1]
    with open(path, 'r') as file:
        parser = SleepParser(quiet=True)
        print(format(parser.parse(file.read(), tracking=True)))
else:
    print('{} <path>'.format(sys.argv[0]))