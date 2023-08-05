# A parser for data encoded (approximately) according to Rivest's sexp format specification

from ZestyParser import *
import binascii, re, sys

t_verbatim_string = Token(r'([0-9]+):', group=1, callback=(lambda p, r: p.scan(TakeToken(int(r)) ^ 'Not enough characters')))
t_token_string = Token(r'[A-Za-z\-./_:*+=][0-9A-Za-z\-./_:*+=]*', group=0)
t_base64_string = Token(r'\|([0-9A-Za-z+/=\s]*)\|', group=1, callback=binascii.a2b_base64)
t_hex_string = Token(r'#([0-9A-Fa-f\s]*)#', group=1, callback=(lambda r: binascii.a2b_hex(re.sub('\s', '', m))))

escapeVals = dict({'\r\n':'', '\n\r':'', '\r':'', '\n':''}, b=chr(8), t=chr(9), v=chr(11), n=chr(10), f=chr(12), r=chr(13))
@CallbackFor(Token(r'"((?:\\.|[^"])*)', group=1) + (RawToken('"') ^ 'Expected quote'))
def t_quoted_string(r):
    text = re.sub(r'\\([0-7]{3})', lambda m: chr(int(m.group(1), 8)), r[0])
    text = re.sub(r'\\x([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), text)
    text = re.sub(r'\\(' + '|'.join(escapeVals.keys()) + ')', lambda m: escapeVals[m.group(1)], text)
    return re.sub(r'\\(.)', r'\1', text)

t_string = t_verbatim_string | t_quoted_string | t_token_string | t_base64_string | t_hex_string
t_list = (RawToken('(') + Only(TokenSeries(Defer(lambda:t_sexp), skip=Token(r'\s+'))) + (RawToken(')') ^ 'Expected close paren or S-expression'))
t_sexp = t_string | t_list

def parse(string):
    return ZestyParser(string).scan(t_sexp ^ 'Expected S-expression')

if __name__ == '__main__':
    print parse(sys.stdin.read())