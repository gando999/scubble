import sys

import parser
from interpreter import Interpreter


if sys.version_info[0] >= 3:
    raw_input = input

if len(sys.argv) == 2:
    data = open(sys.argv[1]).read()
    try:
        prog = parser.parse(data)
    except SyntaxError as se:
        print 'Parse Error: {0}'.format(se)
    if not prog:
        raise SystemExit
    inter = Interpreter(parser.current_scope)
    try:
        inter.run(prog)
        raise SystemExit
    except RuntimeError as re:
        print 'Error: {0}'.format(re)
        raise SystemExit
else:
    inter = Interpreter(parser.current_scope)


def execute_command(name):
    if name == 'load':
        print 'To be implemented'
    elif name == 'resources':
        inter.show_resources()
    elif name == 'quit' or name == 'exit' or name == 'q':
        raise SystemExit
    else:
        print 'Unrecognised command'


while True:
    try:
        line = raw_input("(scubble)> ")
    except EOFError:
        raise SystemExit
    if not line:
        continue
    if line.startswith(':'):
        command = line[1:]
        execute_command(command)
        continue
    try:
        program = parser.parse(line)
    except SyntaxError as se:
        print 'Parse Error: {0}'.format(se)
        continue
    try:
        results = inter.run(program)
    except RuntimeError as re:
        print 'Runtime Error: {0}'.format(re)
        continue
    except TypeError as te:
        print 'Type Error: {0}'.format(te)
        continue
    for r in results:
        if r:
            print r
