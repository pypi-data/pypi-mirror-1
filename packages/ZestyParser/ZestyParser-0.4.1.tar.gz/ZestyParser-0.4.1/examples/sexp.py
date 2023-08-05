# A parser for data encoded (approximately) according to Rivest's sexp format specification

from ZestyParser import *
from sys import stdin
import binascii, re

T_OPEN_PAREN = Token(r'\(')
T_CLOSE_PAREN = Token(r'\)')
T_SPACE = Token(r'\s+')
T_QUOTE = Token(r'"')

T_VERBATIM_STRING = Token(r'([0-9]+):', lambda p, m: p.take(int(m.group(1))))
T_TOKEN_STRING = Token(r'([A-Za-z\-./_:*+=][0-9A-Za-z\-./_:*+=]*)', ReturnRaw)

@CallbackFor(Token(r'#([0-9A-Fa-f\s]*)#'))
def T_HEX_STRING(parser, matches, c):
	h = re.sub('\s', '', matches.group(1))
	if len(h) % 2 == 1: raise ParseError(parser, 'Number of hex digits must be even')
	return binascii.a2b_hex(h)

T_BASE64_STRING = Token(r'\|([0-9A-Za-z+/=\s]*)\|', lambda m: binascii.a2b_base64(m.group(1)))

escapeVals = {
	'b': chr(8),
	't': chr(9),
	'v': chr(11),
	'n': chr(10),
	'f': chr(12),
	'r': chr(13),
	'\r\n': '',
	'\n\r': '',
	'\r': '',
	'\n': '',
}

@CallbackFor(Token(r'"((?:\\.|[^"])*)'))
def T_QUOTED_STRING(parser, matches):
	if not parser.scan(T_QUOTE): raise ParseError(parser, 'Expected double quote, got EOF')
	text = matches.group(1)
	text = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m.group(1), 8)), text)
	text = re.sub(r'\\x([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), text)
	text = re.sub(r'\\(' + '|'.join(escapeVals.keys()) + ')', lambda m: escapeVals[m.group(1)], text)
	text = re.sub(r'\\(.)', r'\1', text)
	return text

T_STRING = T_VERBATIM_STRING | T_QUOTED_STRING | T_TOKEN_STRING | T_BASE64_STRING | T_HEX_STRING

def T_LIST(parser, c):
	if not parser.scan([T_OPEN_PAREN]): raise NotMatched
	o = []
	for t in parser.iter([T_SEXP, T_SPACE, T_CLOSE_PAREN, EOF]):
		if parser.last is T_SEXP: o.append(t)
		elif parser.last is T_CLOSE_PAREN: return o
		elif parser.last is EOF: raise ParseError(parser, 'Expected close paren, got EOF')
	raise ParseError(parser, 'Expected close paren, got unexpected token')

T_SEXP = T_STRING | T_LIST

class SexpParser:
	def __init__(self): self.parser = ZestyParser()
	
	def parse(self, data):
		self.parser.useData(data)
		return self.parser.scan(T_SEXP)

if __name__ == '__main__':
	parser = SexpParser()
	print parser.parse(stdin.read())