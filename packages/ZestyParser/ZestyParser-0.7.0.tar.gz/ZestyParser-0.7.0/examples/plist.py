# Parses the old-style ascii encoding of Apple's plist format

from ZestyParser import *
from sys import stdin
import binascii, re

d_item = Defer(lambda:t_item)
t_sp = Token(r'\s*')
t_quoted_string = (Only(Token(r'"((?:\\.|[^"])*)', group=1)) + (RawToken('"') ^ 'Expected quote')) >> (lambda r: r.replace(r'\"', '"').replace(r'\\', '\\'))
t_inline_string = Token(r'\w+', group=0)
t_data = Token(r'<([0-9a-fA-F\s]*)>', group=1, callback=(lambda m: binascii.a2b_hex(re.sub('\s', '', m))))
t_array = (RawToken('(') + Only(TokenSeries(d_item, skip=t_sp, delimiter=Token(','))) + RawToken(')'))
t_dict = (RawToken('{') + Only(TokenSeries(d_item + Omit(Token('\s*=\s*') ^ 'Expected equal sign') + (d_item ^ 'Expected value'), skip=t_sp, postfix=(Token('\s*;') ^ 'Expected semicolon'), to=dict)) + (RawToken('}') ^ 'Expected close brace or item'))

t_item = t_quoted_string | t_inline_string | t_data | t_array | t_dict

parser = ZestyParser(stdin.read())
print parser.scan(t_item)