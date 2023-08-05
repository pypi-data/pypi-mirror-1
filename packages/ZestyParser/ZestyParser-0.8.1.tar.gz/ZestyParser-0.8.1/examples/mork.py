# This isn't really tested. I could only find a specification for version "1.1", and I couldn't find any Mork files of that version (only newer ones). And I certainly don't feel like deciphering the newer versions. So if you know where I might find some 1.1 encoded files, let me know!

from ZestyParser import *
from ZestyParser.Helpers import *

r_line_end = r'\r\n|\n\r|[\r\n]'

line_end = RE(r'(?:' + r_line_end + ')')
sp = Skip(RE(r'(?:[ \t\r\n]|(?:\\%(l)s)|//[^\r\n](?:%(l)s))' % {'l': r_line_end}))
Helpers.default_whitespace = sp.desc

magic = Raw('// <!-- <mdb:mork:z v="1.1"/> -->')
id_ = RE(r'[0-9a-fA-F]+')

table_ref = sp + Raw('t') + id_
row_ref = sp + Raw('r') + id_
value_ref = sp + Raw('^') + id_
any_ref = table_ref | row_ref | value_ref

name = RE(r'[a-zA-Z:_][a-zA-Z:_+\-?!]*')
value = Raw('=') + RE(r'(?:[^)]|\\.)')

cell = EncloseHelper('()', (name | value_ref) + (value | any_ref | Default(None)))

dict_ = EncloseHelper('<>', Inf*(
    EncloseHelper('<>', cell*Inf) |
    EncloseHelper('()', id_ - value) |
))

meta_table = EncloseHelper('{}', cell*Inf)
meta_row = EncloseHelper('[]', cell*Inf)

row_item = (id_ + (meta_row | cell)*Inf)
row = EncloseHelper('[]', row_item)

table = EncloseHelper('{}', (id_ + (meta_table | row_ref | row)*Inf))
update = sp + RE(r'[!+\-]') + (row | table)
header = EncloseHelper(('@[', ']@'), id_ - (row_item)*Inf)

content = TokenSeries(dict_ | table | update)

group = sp + Raw('@$${') + id_ + Raw('{@') + content - Raw('@$$}') + (Raw('~abort~', to=Const(False)) | Default(True)) + id_ + Raw('}@')

mork = magic + line_end + header + (content | group)

def parse(string):
    return DebuggingParser(string).scan(mork + (EOF ^ 'Unexpected data'))

if __name__ == '__main__':
    print parse(sys.stdin.read())