from ZestyParser import *

t_paren_expr = (RawToken('(') + Only(Defer(lambda:t_expr)) + RawToken(')'))
t_factor = (t_paren_expr | Token('([0-9]*\.[0-9]+|[0-9]+)', group=0, to=float))

t_term = Defer(lambda:t_term)
t_term = (
    ((t_factor + RawToken('*') + t_term) >> (lambda r: r[0] * r[2])) |
    ((t_factor + RawToken('/') + t_term) >> (lambda r: r[0] / r[2])) |
    t_factor
)

t_expr = Defer(lambda:t_expr)
t_expr = (
    ((t_term + Omit(RawToken('+')) + t_expr) >> sum) |
    ((t_term + RawToken('-') + t_expr) >> (lambda r: r[0] - r[2])) |
    t_term
)

def evaluate(expression):
    parser = ZestyParser(expression)
    return parser.scan(t_expr)

if __name__ == '__main__':
    from sys import stdin
    print evaluate(stdin.read())