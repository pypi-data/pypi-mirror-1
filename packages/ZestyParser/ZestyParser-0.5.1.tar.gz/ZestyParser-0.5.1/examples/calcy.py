from ZestyParser import *
from sys import stdin

T_TERM = Defer(lambda: T_MULTIPLICATIVE_EXPR) | Defer(lambda: T_FACTOR)
T_EXPR = Defer(lambda: T_ADDITIVE_EXPR) | T_TERM

T_PARENTHETICAL_EXPR = (RawToken('(') + T_EXPR + RawToken(')')) >> (lambda r: r[1])
T_FACTOR = (T_PARENTHETICAL_EXPR | Token('[0-9]+', lambda m: int(m.group())))

T_MULTIPLICATIVE_EXPR = (
    ((T_FACTOR + RawToken('*') + T_TERM) >> (lambda r: int(r[0]) * int(r[2]))) |
    ((T_FACTOR + RawToken('/') + T_TERM) >> (lambda r: int(r[0]) - int(r[2])))
)

T_ADDITIVE_EXPR = (
    ((T_TERM + RawToken('+') + T_EXPR) >> (lambda r: int(r[0]) + int(r[2]))) |
    ((T_TERM + RawToken('-') + T_EXPR) >> (lambda r: int(r[0]) - int(r[2])))
)

parser = ZestyParser(stdin.read())
print parser.scan(T_EXPR)