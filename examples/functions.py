# -*- coding: utf-8 -*-
# Show information about function usage in a sleep script.

import sys
from sleepy.parser import *

if len(sys.argv) > 1:
    path = sys.argv[1]
    with open(path, 'r') as file:
        parser = SleepParser(quiet=True)
        script = parser.parse(file.read(), tracking=True)
        functions = script.functions()
        print('Functions: ' + ', '.join(functions) if len(functions) > 0 else 'None')
        xrefs = script.xrefs()
        if len(xrefs) > 0:
            print('\nCross references:')
            for function, calls in sorted(xrefs.items()):
                print('  ' + (function if function else 'Main Script') + ' -> ' + ', '.join(calls) if len(calls) > 0 else 'None')
else:
    print('{} <path>'.format(sys.argv[0]))