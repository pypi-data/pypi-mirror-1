from ZestyParser import *
import re
from sys import stdin

T_HELLO = Token('(?i)hello', group=0)
T_SP = Token('\s+', group=0)
T_WORLD = Token('(?i)world', group=0)
T_EXCL = Token('\!', group=0)

p = ZestyParser(stdin.read())

for t in p.iter((T_HELLO, T_SP, T_WORLD, T_EXCL)):
	print t
