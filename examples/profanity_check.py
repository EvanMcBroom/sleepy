# -*- coding: utf-8 -*-
# Generate a report of profanity in a text file.

import pathlib
import sys
from profanity_check import predict

if len(sys.argv) > 1:
    path = sys.argv[1]
    for path in pathlib.Path('.').glob(path):
        print('Checking: {}'.format(path))
        with open(path, 'r') as file:
            lines = [line.rstrip() for line in file]
            for index, result in enumerate(predict(lines)):
                if result:
                    print('- detected ({}): {}'.format(index + 1, lines[index]))
else:
    print('{} <path glob>'.format(sys.argv[0]))