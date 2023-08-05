from ZestyParser import *
import re
from sys import stdin

T_HELLO = Token(re.compile('hello', re.IGNORECASE))
T_SP = Token('\s+')
T_WORLD = Token(re.compile('world', re.IGNORECASE))
T_EXCL = Token('\!')

tokens = (T_HELLO, T_SP, T_WORLD, T_EXCL)

p = ZestyParser(stdin.read())

for t in p.iter(tokens):
	print t
