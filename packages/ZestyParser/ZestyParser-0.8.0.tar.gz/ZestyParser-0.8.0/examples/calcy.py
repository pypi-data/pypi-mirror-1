from __future__ import division
from ZestyParser import *
from ZestyParser.Helpers import *
import operator as op

t_expression = ExpressionHelper((
    Float | Int,
    EncloseHelper('()', _top_), #it's PEMDAS time!
    oper('+', op.pos, UNARY) | oper('-', op.neg, UNARY),
    oper('!', (lambda v: reduce(op.mul, range(1,v+1), 1)), UNARY, RIGHT),
    oper('^', op.pow),
    oper('*', op.mul) | oper('/', op.truediv),
    oper('+', op.add) | oper('-', op.sub),
))

def evaluate(expression):
    parser = ZestyParser(expression)
    return parser.scan(t_expression)

if __name__ == '__main__':
    from sys import stdin
    print evaluate(stdin.read())