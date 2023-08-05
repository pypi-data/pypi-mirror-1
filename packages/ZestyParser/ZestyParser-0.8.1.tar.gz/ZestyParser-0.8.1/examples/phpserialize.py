# Parses data in PHP's serialize format (minus PHP objects, of course)

from ZestyParser import *
from sys import stdin

t_quote = Raw('"') ^ 'Expected quote'

t_string = RE(r's:([0-9]+):', group=1, callback=(lambda p, m: p.scan(t_quote + Only(TakeToken(int(m)) ^ 'Not enough characters') + t_quote + (Raw(';') ^ 'Expected semicolon'))))
t_integer = RE(r'i:([0-9]+);', group=1, to=int)
t_bool = RE(r'b:(0|1);', group=1, to=bool)
t_null = Raw('N;', to=Const(None))
t_double = RE(r'd:([0-9\.]+);', group=1, to=float)

t_value = t_string | t_integer | t_bool | t_null | t_double | Defer(lambda:t_array)

@CallbackFor(
    RE(r'a:([0-9]+):{') +
    Only(TokenSeries(t_value + (t_value ^ 'Expected second value'), to=dict)) +
    (Raw('}') ^ 'Expected close brace or value')
)
def t_array(r):
    if r.keys() == range(len(r)): return r.values()
    else: return r

def parse(string):
    return ZestyParser(string).scan(t_value ^ 'Expected value')

if __name__ == '__main__':
    print parse(stdin.read())