import sys
import pprint
from sleepy.parser import *

if len(sys.argv) > 1:
    path = sys.argv[1]
    with open(path, 'r') as file:
        parser = SleepParser(quiet=True)
        pprint.pprint(parser.parse(file.read(), tracking=True))
else:
    print('{} <path>'.format(sys.argv[0]))