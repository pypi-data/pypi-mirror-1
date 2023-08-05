# A small parser for data in BitTorrent's bencode format.

from ZestyParser import *
from sys import stdin

T_BYTESTRING = Token('([0-9]+):', lambda p, m: p.scan(TakeToken(int(m.group(1)))))
T_INTEGER = Token('i(0|-?[1-9][0-9]*)e', lambda m: int(m.group(1)))
T_LIST = (RawToken('l') + TokenSeries(Defer(lambda: T_ITEM)) + (RawToken('e') ^ 'Expected "e" or item')) >> (lambda r: r[1])
T_DICT = (RawToken('d') + TokenSeries(Defer(lambda: T_ITEM) + (Defer(lambda: T_ITEM) ^ 'Expected second value')) + (RawToken('e') ^ 'Expected "e" or item')) >> (lambda r: dict(r[1]))

T_ITEM = T_BYTESTRING | T_INTEGER | T_LIST | T_DICT

parser = ZestyParser(stdin.read())
print parser.scan(T_ITEM)