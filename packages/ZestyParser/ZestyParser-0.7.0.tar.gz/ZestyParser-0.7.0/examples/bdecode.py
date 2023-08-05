# A small parser for data in BitTorrent's bencode format.

from ZestyParser import *
from sys import stdin

d_item = Defer(lambda:t_item)
t_bytestring = Token('([0-9]+):', group=1, callback=(lambda p, m: p.scan(TakeToken(int(m)))))
t_integer = Token('i(0|-?[1-9][0-9]*)e', group=1, to=int)
t_list = (Omit(RawToken('l')) + TokenSeries(d_item, until=(RawToken('e'), 'Expected e'))) >> list.pop
t_dict = (Omit(RawToken('d')) + TokenSeries(d_item + (d_item ^ 'Expected second value'), to=dict, until=(RawToken('e'), 'Expected e'))) >> list.pop

t_item = t_bytestring | t_integer | t_list | t_dict

parser = ZestyParser(stdin.read())
print parser.scan(t_item)