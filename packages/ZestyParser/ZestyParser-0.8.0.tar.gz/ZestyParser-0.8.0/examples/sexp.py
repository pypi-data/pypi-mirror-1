# A parser for data encoded (approximately) according to Rivest's sexp format specification
# Not included: display hints (because they're stupid) and length prefices for non-verbatim strings (because they're stupid)

from ZestyParser import *
from ZestyParser.Helpers import *
from binascii import a2b_base64, a2b_hex
import re, sys

t_verbatim_string = RE(r'([0-9]+):', group=1, callback=(lambda p, r: p.scan(TakeToken(int(r)) ^ 'Not enough characters')))
t_token_string = RE(r'[A-Za-z\-./_:*+=][0-9A-Za-z\-./_:*+=]*', group=0)
t_base64_string = RE(r'\|([0-9A-Za-z+/=\s]*)\|', group=1, to=a2b_base64)
t_hex_string = RE(r'#([0-9A-Fa-f\s]*)#', group=1, to=(lambda r: a2b_hex(re.sub(r'\s', '', r))))

t_quoted_string = QuoteHelper(quotes='"') >> EscapeHelper(
    (r'\\([0-7]{3})', FromOct),
    (r'\\x([0-9A-Fa-f]{2})', FromHex),
    (EscCh(chars='btvnfr\r\n'), PyEsc),
    (EscCh(anything=True), SameChar),
)

t_string = t_verbatim_string | t_quoted_string | t_token_string | t_base64_string | t_hex_string
t_list = EncloseHelper('()', TokenSeries(Placeholder(), skip=RE(r'\s+')))
t_sexp = t_string | t_list
t_list %= t_sexp

def parse(string):
    return ZestyParser(string).scan(t_sexp ^ 'Expected S-expression')

if __name__ == '__main__':
    print parse(sys.stdin.read())