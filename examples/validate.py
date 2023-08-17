import sys
from sleepy.parser import *

if len(sys.argv) > 1:
    path = sys.argv[1]
    with open(path, 'r') as file:
        parser = SleepParser()
        parser.parse(file.read(), tracking=True)
else:
    print('{} <path>'.format(sys.argv[0]))