# Parses data in PHP's serialize format (minus PHP objects, of course)

from ZestyParser import *
from sys import stdin

T_CLOSE_BRACE = RawToken('}')
T_QUOTE = RawToken('"')

T_STRING = Token(r's:([0-9]+):', lambda p, m: p.scan((T_QUOTE ^ 'Expected quote') + (TakeToken(int(m.group(1))) ^ 'Not enough characters') + (T_QUOTE ^ 'Expected quote') + (RawToken(';') ^ 'Expected semicolon'))[1])
T_INTEGER = Token(r'i:([0-9]+);', lambda m: int(m.group(1)))
T_BOOL = Token(r'b:(0|1);', lambda m: bool(m.group(1)))
T_NULL = RawToken('N;', lambda m: None)
T_DOUBLE = Token(r'd:([0-9.]+);', lambda m: float(m.group(1)))

@CallbackFor(Token(r'a:([0-9]+):{'))
def T_ARRAY(parser, m):
    o = dict(parser.iter(T_VALUE + (T_VALUE ^ 'Expected second value')))

    parser.skip(T_CLOSE_BRACE ^ 'Expected close brace or value')
    if o.keys() == range(len(o)): return o.values()
    else: return o

T_VALUE = T_STRING | T_INTEGER | T_ARRAY | T_BOOL | T_NULL | T_DOUBLE

def parse(string):
    return ZestyParser(string).scan(T_VALUE ^ 'Expected value')

if __name__ == '__main__':
    print parse(stdin.read())