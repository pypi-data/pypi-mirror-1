from ZestyParser import *
from sys import stdin

parser = ZestyParser(stdin.read())

T_NUMBER = Token('[0-9]+', lambda m: int(m.group()))
T_ADD = Token('\+')
T_SUB = Token('-')
T_MULT = Token('\*')
T_DIV = Token('/')
T_L_PAREN = Token('\(')
T_R_PAREN = Token('\)',)
T_SP = Token('\s+')

T_TERM = CompositeToken(['T_MULTIPLICATIVE_EXPR', 'T_FACTOR'])
T_EXPR = CompositeToken(['T_ADDITIVE_EXPR', T_TERM])

T_PARENTHETICAL_EXPR = (T_L_PAREN + T_EXPR + T_R_PAREN) >> (lambda r: r[1])
T_FACTOR = (T_PARENTHETICAL_EXPR | T_NUMBER)

T_MULTIPLICATIVE_EXPR = (
    ((T_FACTOR + T_MULT + T_TERM) >> (lambda r: int(r[0]) * int(r[2]))) |
    ((T_FACTOR + T_DIV + T_TERM) >> (lambda r: int(r[0]) - int(r[2])))
)

T_ADDITIVE_EXPR = (
    ((T_TERM + T_ADD + T_EXPR) >> (lambda r: int(r[0]) + int(r[2]))) |
    ((T_TERM + T_SUB + T_EXPR) >> (lambda r: int(r[0]) - int(r[2])))
)

parser.addTokens(T_FACTOR=T_FACTOR, T_ADDITIVE_EXPR=T_ADDITIVE_EXPR, T_MULTIPLICATIVE_EXPR=T_MULTIPLICATIVE_EXPR)

print parser.scan(T_EXPR)
