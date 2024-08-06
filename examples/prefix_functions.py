# -*- coding: utf-8 -*-

import json
import sys
import sleepy.ast
from sleepy.parser import *

internalFunctions = list()

def visitor(node):
    if isinstance(node, Call) and node.function in internalFunctions:
        node.function = prefix + node.function
    return node

if len(sys.argv) > 2:
    prefix = sys.argv[1]
    path = sys.argv[2]
    with open(path, 'r') as file:
        parser = SleepParser(quiet=True)
        script = parser.parse(file.read(), tracking=True)
        # Filter any empty statements that may have been generated by syntax errors
        script.body = [_ for _ in script.body if _]
        # First enumerate and rename all first level internal functions to have a prefix
        for index, statement in enumerate(script.body):
            if isinstance(statement, EnvBridge) and statement.keyword == 'sub':
                internalFunctions.append(statement.identifier)
                statement.identifier = prefix + statement.identifier
                script.body[index] = statement
        # Then update each instance where an internal function
        newScript = walk(script, visitor)
        print(sleepy.ast.format(newScript))
else:
    print('{} <prefix> <path>'.format(sys.argv[0]))