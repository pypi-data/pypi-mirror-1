# Parses data in PHP's serialize format (minus PHP objects, of course)

from ZestyParser import *
from sys import stdin

T_QUOTE = RawToken('"')

T_STRING = Token(r's:([0-9]+):', lambda p, m: p.scan((T_QUOTE ^ 'Expected quote') + (TakeToken(int(m.group(1))) ^ 'Not enough characters') + (T_QUOTE ^ 'Expected quote') + (RawToken(';') ^ 'Expected semicolon'))[1])
T_INTEGER = Token(r'i:([0-9]+);', group=1, as=int)
T_BOOL = Token(r'b:(0|1);', group=1, as=bool)
T_NULL = RawToken('N;', lambda m: None)
T_DOUBLE = Token(r'd:([0-9.]+);', group=1, as=float)

T_VALUE = T_STRING | T_INTEGER | T_BOOL | T_NULL | T_DOUBLE | Defer(lambda: T_ARRAY)

@CallbackFor(Token(r'a:([0-9]+):{') + TokenSeries(T_VALUE + (T_VALUE ^ 'Expected second value')) + (RawToken('}') ^ 'Expected close brace or value'))
def T_ARRAY(parser, r):
    o = dict(r[1])
    if o.keys() == range(len(o)): return o.values()
    else: return o

def parse(string):
    return ZestyParser(string).scan(T_VALUE ^ 'Expected value')

if __name__ == '__main__':
    print parse(stdin.read())