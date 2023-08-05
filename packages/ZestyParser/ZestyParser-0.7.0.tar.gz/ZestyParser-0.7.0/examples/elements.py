from ZestyParser import *
from sys import stdin

t_formula = TokenSeries(
    Token('[A-Z][a-z]*', group=0) +
    (Token('[1-9][0-9]*', group=0, to=int) | Default(1)),
min=1)

parser = ZestyParser(stdin.read())
print parser.scan(t_formula)