# Parses the old-style ascii encoding of Apple's plist format

from ZestyParser import *
from sys import stdin
import binascii, re

d_item = Defer(lambda:t_item)
t_sp = RE(r'\s*')
t_quoted_string = QuoteHelper(quotes='"')
t_inline_string = RE(r'\w+', group=0)
t_data = RE(r'<([0-9a-fA-F\s]*)>', group=1, to=(lambda m: binascii.a2b_hex(re.sub('\s', '', m))))
t_array = EncloseHelper('()', TokenSeries(d_item, skip=t_sp, delimiter=Raw(',')))
t_dict = EncloseHelper('{}', TokenSeries(d_item + Omit(RE('\s*=\s*') ^ 'Expected equal sign') + (d_item ^ 'Expected value'), skip=t_sp, postfix=(RE('\s*;') ^ 'Expected semicolon'), to=dict))

t_item = t_quoted_string | t_inline_string | t_data | t_array | t_dict

parser = ZestyParser(stdin.read())
print parser.scan(t_item)