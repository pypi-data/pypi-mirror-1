from ZestyParser import *
import re
from sys import stdin

T_QUOTE = Token('quote', r'"')
T_CHAR = Token('cdata', r'[^\\"]+', ReturnRaw)
T_ESCAPED = Token('escaped', r'\\(.)', lambda p, m, c: m.group(1))

def T_STRING(parser, c):
	if not parser.scan([T_QUOTE]): raise NotMatched
	o = []
	for t in parser.iter([T_ESCAPED, T_CHAR, T_QUOTE, EOF]):
		if t[0] in (T_ESCAPED, T_CHAR):
			o.append(t[1])
		elif t[0] is T_QUOTE:
			break
		elif t[0] is EOF:
			raise NotMatched
	return ''.join(o)

parser = ZestyParser(stdin.read())
print parser.scan([T_STRING])
