# A small parser for data in BitTorrent's bencode format.

from ZestyParser import *
from sys import stdin

parser = ZestyParser(stdin.read())

T_BYTESTRING = Token('([0-9]+):', lambda p, m: p.take(int(m.group(1))))
T_INTEGER = Token('i(0|-?[1-9][0-9]*)e', lambda m: int(m.group(1)))
T_E = Token('e')

@CallbackFor(Token('(l|d)'))
def T_LIST(parser, m):
    asDict = (m.group(1) == 'd')
    o = []
    for t in parser.iter([T_ITEM, T_E, EOF]):
        if parser.last is T_ITEM: o.append(t)
        elif parser.last is T_E:
            if asDict: return dict(zip(o[::2], o[1::2]))
            else: return o
        elif parser.last is T_EOF: raise ParseError(parser, 'Expected "e", got EOF')
    raise ParseError(parser, 'Expected "e", got unexpected data')

T_ITEM = T_BYTESTRING | T_INTEGER | T_LIST

print parser.scan(T_ITEM)