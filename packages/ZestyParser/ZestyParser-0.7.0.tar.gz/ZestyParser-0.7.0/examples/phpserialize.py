# Parses data in PHP's serialize format (minus PHP objects, of course)

from ZestyParser import *
from sys import stdin

t_quote = RawToken('"') ^ 'Expected quote'

t_string = Token(r's:([0-9]+):', group=1, callback=(lambda p, m: p.scan(t_quote + Only(TakeToken(int(m)) ^ 'Not enough characters') + t_quote + (RawToken(';') ^ 'Expected semicolon'))))
t_integer = Token(r'i:([0-9]+);', group=1, to=int)
t_bool = Token(r'b:(0|1);', group=1, to=bool)
t_null = RawToken('N;', to=Const(None))
t_double = Token(r'd:([0-9.]+);', group=1, to=float)

t_value = t_string | t_integer | t_bool | t_null | t_double | Defer(lambda:t_array)

@CallbackFor(Token(r'a:([0-9]+):{') + Only(TokenSeries(t_value + (t_value ^ 'Expected second value'), to=dict)) + (RawToken('}') ^ 'Expected close brace or value'))
def t_array(r):
    if r.keys() == range(len(r)): return r.values()
    else: return r

def parse(string):
    return ZestyParser(string).scan(t_value ^ 'Expected value')

if __name__ == '__main__':
    print parse(stdin.read())