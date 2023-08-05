from ZestyParser import *
from sys import stdin

T_FORMULA = TokenSeries(Token('([A-Z][a-z]*)([1-9][0-9]*)?', lambda r: (r.group(1), int(r.group(2) or 1))), min=1)

parser = ZestyParser(stdin.read())
print parser.scan(T_FORMULA)