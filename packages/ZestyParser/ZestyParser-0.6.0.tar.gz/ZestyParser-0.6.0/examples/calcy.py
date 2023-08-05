from ZestyParser import *
from sys import stdin

T_TERM = Defer(lambda: T_MULTIPLICATIVE_EXPR) | Defer(lambda: T_FACTOR)
T_EXPR = Defer(lambda: T_ADDITIVE_EXPR) | T_TERM

T_PARENTHETICAL_EXPR = (Omit(RawToken('(')) + T_EXPR + Omit(RawToken(')'))) >> min
T_FACTOR = (T_PARENTHETICAL_EXPR | Token('[0-9]+', group=0, as=int))

T_MULTIPLICATIVE_EXPR = (
    ((T_FACTOR + Omit(RawToken('*')) + T_TERM) >> (lambda r: r[0] * r[1])) |
    ((T_FACTOR + Omit(RawToken('/')) + T_TERM) >> (lambda r: r[0] / r[1]))
)

T_ADDITIVE_EXPR = (
    ((T_TERM + Omit(RawToken('+')) + T_EXPR) >> (lambda r: r[0] + r[1])) |
    ((T_TERM + Omit(RawToken('-')) + T_EXPR) >> (lambda r: r[0] - r[1]))
)

parser = ZestyParser(stdin.read())
print parser.scan(T_EXPR)