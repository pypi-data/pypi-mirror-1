# A small parser for data in BitTorrent's bencode format.

from ZestyParser import *
from ZestyParser.Helpers import *
from sys import stdin

d_item = Defer(lambda:t_item)
t_bytestring = RE('([0-9]+):', group=1, callback=(lambda p, m: p.scan(TakeToken(int(m)))))
t_integer = RE('i(0|-?[1-9][0-9]*)e', group=1, to=int)
t_list = EncloseHelper('le', Inf*d_item)
t_dict = EncloseHelper('de', TokenSeries(d_item + (d_item ^ 'Expected second value'), to=dict))

t_item = t_bytestring | t_integer | t_list | t_dict

parser = ZestyParser(stdin.read())
print parser.scan(t_item)