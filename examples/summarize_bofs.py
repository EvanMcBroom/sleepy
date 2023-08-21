import json
import sys
from sleepy.parser import *

bofs = {}
if len(sys.argv) > 1:
    path = sys.argv[1]
    with open(path, 'r') as file:
        parser = SleepParser(quiet=True)
        script = parser.parse(file.read(), tracking=True)
        # Filter any empty statements that may have been generated by syntax errors
        script.body = [_ for _ in script.body if _]
        # Enumerate all of the declared beacon commands that use a bof
        for statement in script.body:
            # First enumerate all beacon commands
            if isinstance(statement, EnvBridge) and statement.keyword == 'alias':
                aliasBridge = statement
                bofFile = None
                argFormat = ''
                command = aliasBridge.identifier
                # Enumerate all statements in the alias's body
                # Check for if any use bof_pack or beacon_inline_execute
                # We're making the assumption these will only happen at most once
                for statement in aliasBridge.body:
                    # We're making the assumption this will only happen once
                    if isinstance(statement, BinOp) and statement.op == '=':
                        rhs = statement.right
                        if isinstance(rhs, Call) and rhs.function == 'bof_pack':
                            argFormat = rhs.args[1].value
                    # Check if one of the statements is used to run beacon_inline_execute
                    if isinstance(statement, Call) and statement.function == 'beacon_inline_execute':
                        bofArg = statement.args[1].value
                        if isinstance(bofArg, Call) and bofArg.function == 'readbof':
                            bofFile = bofArg.args[1].value
                if bofFile:
                    bofs[bofFile] = {
                        'arg_format': argFormat
                    }
        # Enumerate all of the registered help information for a bof
        # We're assuming that the bof name matches the command name for the help information
        for statement in script.body:
            if isinstance(statement, Call) and statement.function == 'beacon_command_register':
                args = statement.args
                if args[0].value in bofs:
                    bofs[args[0].value]['help_short'] = args[1].value
                    bofs[args[0].value]['help_long'] = args[2].value
    print(json.dumps(bofs, indent=4))
else:
    print('{} <path>'.format(sys.argv[0]))