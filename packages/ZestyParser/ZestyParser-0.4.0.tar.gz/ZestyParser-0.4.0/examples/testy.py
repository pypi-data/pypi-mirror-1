from ZestyParser import *
import re
from sys import stdin

T_HELLO = Token('hello', re.compile('hello', re.IGNORECASE))
T_SP = Token('space', '\s+')
T_WORLD = Token('world', re.compile('world', re.IGNORECASE))
T_EXCL = Token('excl', '\!')

tokens = (T_HELLO, T_SP, T_WORLD, T_EXCL)

p = ZestyParser(stdin.read())

for t in p.iter(tokens):
	print t
