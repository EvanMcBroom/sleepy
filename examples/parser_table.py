# -*- coding: utf-8 -*-
# Show the parsing table (e.g., the grammer rules) for sleepy's parser.

from sleepy.parser import *
import inspect

SleepParser(debug=True)
with open(os.sep.join(inspect.getfile(SleepParser).split(os.sep)[:-1] + ['parser.out']), 'r') as file:
    print(file.read())