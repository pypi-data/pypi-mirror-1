# A parser for data encoded (approximately) according to Rivest's sexp format specification

from ZestyParser import *
import binascii, re, sys

T_VERBATIM_STRING = Token(r'([0-9]+):', lambda p, m: p.scan(TakeToken(int(m.group(1))) ^ 'Not enough characters'))
T_TOKEN_STRING = Token(r'[A-Za-z\-./_:*+=][0-9A-Za-z\-./_:*+=]*', ReturnRaw)
T_BASE64_STRING = Token(r'\|([0-9A-Za-z+/=\s]*)\|', lambda m: binascii.a2b_base64(m.group(1)))
T_HEX_STRING = Token(r'#([0-9A-Fa-f\s]*)#', lambda m: binascii.a2b_hex(re.sub('\s', '', m.group(1))))

escapeVals = { 'b':chr(8), 't':chr(9), 'v':chr(11), 'n':chr(10), 'f':chr(12), 'r':chr(13), '\r\n':'', '\n\r':'', '\r':'', '\n':'' }
@CallbackFor(Token(r'"((?:\\.|[^"])*)', lambda m: m.group(1)) + (RawToken('"') ^ 'Expected quote'))
def T_QUOTED_STRING(r):
	text = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m.group(1), 8)), r[0])
	text = re.sub(r'\\x([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), text)
	text = re.sub(r'\\(' + '|'.join(escapeVals.keys()) + ')', lambda m: escapeVals[m.group(1)], text)
	return re.sub(r'\\(.)', r'\1', text)

T_STRING = T_VERBATIM_STRING | T_QUOTED_STRING | T_TOKEN_STRING | T_BASE64_STRING | T_HEX_STRING
T_LIST = (RawToken('(') + TokenSeries(Defer(lambda: T_SEXP), skip=Token(r'\s+')) + (RawToken(')') ^ 'Expected close paren or S-expression')) >> (lambda r: r[1])
T_SEXP = T_STRING | T_LIST

def parse(string):
    return ZestyParser(string).scan(T_SEXP ^ 'Expected S-expression')

if __name__ == '__main__':
	print parse(sys.stdin.read())