from ZestyParser import *
from ZestyParser.Helpers import *

t = Only(Raw('hello')) + (Raw('\n') ^ 'Expected newline')

b = IndentHelper(t | Placeholder())
b %= RE(r'zeet\n?') + Only(b)

import sys
inp = '''hello
zeet
 hello
 zeet
  hello
zeet
 hello
 hello
 zeet
   hello
   hello
hello
zeet hello
     hello
'''
#print ZestyParser(sys.stdin.read()).scan(b)
print ZestyParser(inp).scan(b)