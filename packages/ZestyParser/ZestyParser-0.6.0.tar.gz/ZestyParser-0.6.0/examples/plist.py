# Parses the old-style ascii encoding of Apple's plist format

from ZestyParser import *
from sys import stdin
import binascii, re

D_ITEM = Defer(lambda: T_ITEM)
T_SP = Token(r'\s*')
T_QUOTED_STRING = (Token(r'"((?:\\.|[^"])*)') + (RawToken('"') ^ 'Expected quote')) >> (lambda r: r[0].group(1).replace(r'\"', '"').replace(r'\\', '\\'))
T_INLINE_STRING = Token(r'\w+', group=0)
T_DATA = Token(r'<([0-9a-fA-F\s]*)>', group=1, callback=(lambda m: binascii.a2b_hex(re.sub('\s', '', m))))
T_ARRAY = (RawToken('(') + TokenSeries(D_ITEM, skip=T_SP, delimiter=Token(',')) + RawToken(')')) >> (lambda r: r[1])
T_DICT = (RawToken('{') + TokenSeries(D_ITEM + Omit(Token('\s*=\s*') ^ 'Expected equal sign') + (D_ITEM ^ 'Expected value'), skip=T_SP, postfix=(Token('\s*;') ^ 'Expected semicolon')) + (RawToken('}') ^ 'Expected close brace or item')) >> (lambda r: dict(r[1]))

T_ITEM = T_QUOTED_STRING | T_INLINE_STRING | T_DATA | T_ARRAY | T_DICT

parser = ZestyParser(stdin.read())
print parser.scan(T_ITEM)