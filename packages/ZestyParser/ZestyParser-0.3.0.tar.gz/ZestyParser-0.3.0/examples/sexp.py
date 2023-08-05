from ZestyParser import *
from sys import stdin
import binascii, re

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

T_NUMBER = Token('number', r'[0-9]+', lambda p, m, c: int(m.group()))
T_OPEN_PAREN = Token('open_paren', r'\(')
T_CLOSE_PAREN = Token('close_paren', r'\)')
T_SPACE = Token('space', r'\s+')
T_QUOTE = Token('quote', r'"')
T_CHAR = Token('cdata', r'[^\\"]+', ReturnRaw)
def escapeChar(p, m, c):
	ch = m.group(1)
	if ch in escapeVals:
		return escapeVals[ch]
	else:
		return ch
T_ESCAPED = Token('escaped', r'\\(\r\n|\n\r|.)', escapeChar)
T_ESCAPED_OCTAL = Token('escaped_octal', r'\\([0-7]{3})', lambda p, m, c: chr(int(m.group(1), 8)))
T_ESCAPED_HEX = Token('escaped_hex', r'\\x([0-9A-Fa-f]{2})', lambda p, m, c: chr(int(m.group(1), 16)))

T_VERBATIM_STRING = Token('verbatim', r'([0-9]+):', lambda p, m, c: p.take(int(m.group(1))))
T_TOKEN_STRING = Token('token', r'([A-Za-z\-./_:*+=][0-9A-Za-z\-./_:*+=]*)', ReturnRaw)

def processHexString(parser, matches, c):
	h = re.sub('\s', '', matches.group(1))
	if len(h) % 2 == 1: raise ParseError(parser, 'Number of hex digits must be even')
	return binascii.a2b_hex(h)
T_HEX_STRING = Token('hex_string', r'#([0-9A-Fa-f\s]*)#', processHexString)

T_BASE64_STRING = Token('base64_string', r'\|([0-9A-Za-z+/=\s]*)\|', lambda p, m, c: binascii.a2b_base64(m.group(1)))

def T_QUOTED_STRING(parser, c):
	if not parser.scan([T_QUOTE]): raise NotMatched
	o = []
	for t in parser.iter([T_ESCAPED_OCTAL, T_ESCAPED_HEX, T_ESCAPED, T_CHAR, T_QUOTE, EOF]):
		if t[0] in (T_ESCAPED_OCTAL, T_ESCAPED_HEX, T_ESCAPED, T_CHAR): o.append(t[1])
		elif t[0] is T_QUOTE: break
		elif t[0] is EOF: raise ParseError(parser, 'Expected double quote, got EOF')
	return ''.join(o)

T_STRING = CompositeToken('string', [T_QUOTED_STRING, T_VERBATIM_STRING, T_TOKEN_STRING, T_BASE64_STRING, T_HEX_STRING], lambda p, r, c: r[1])

def T_LIST(parser, c):
	if not parser.scan([T_OPEN_PAREN]): raise NotMatched
	o = []
	for t in parser.iter([T_SEXP, T_SPACE, T_CLOSE_PAREN, EOF]):
		if t[0] is T_SEXP: o.append(t[1])
		elif t[0] is T_CLOSE_PAREN: return o
		elif t[0] is EOF: raise ParseError(parser, 'Expected close paren, got EOF')
	raise ParseError(parser, 'Expected close paren, got unexpected token')

T_SEXP = CompositeToken('sexp', [T_LIST, T_STRING], lambda p, r, c: r[1])

class SexpParser:
	def __init__(self):
		self.parser = ZestyParser()
	
	def parse(self, data):
		self.parser.useData(data)
		return self.parser.scan([T_SEXP])[1]

if __name__ == '__main__':
	parser = SexpParser()
	print parser.parse(stdin.read())