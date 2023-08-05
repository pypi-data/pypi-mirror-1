from ZestyParser import *
from sys import stdin

parser = ZestyParser(stdin.read())
A = parser.addTokens

A(Token('T_NUMBER', '[0-9]+', lambda p, m, c: int(m.group())))
A(Token('T_ADD', '\+'))
A(Token('T_SUB', '-'))
A(Token('T_MULT', '\*'))
A(Token('T_DIV', '/'))
A(Token('T_L_PAREN', '\('))
A(Token('T_R_PAREN', '\)',))
A(Token('T_SP', '\s+'))

A(CompositeToken('T_EXPR', ['T_ADDITIVE_EXPR', 'T_TERM'], ReturnDirect))
A(CompositeToken('T_TERM', ['T_MULTIPLICATIVE_EXPR', 'T_FACTOR'], ReturnDirect))
A(CompositeToken('T_FACTOR', ['T_PARENTHETICAL_EXPR', 'T_NUMBER'], ReturnDirect))

A(TokenSequence('T_PARENTHETICAL_EXPR', [['T_L_PAREN'], ['T_EXPR'], ['T_R_PAREN']], lambda p, r, c: r[1][1]))

A(CompositeToken('T_MULTIPLICATIVE_EXPR',
		 [TokenSequence(None, [['T_FACTOR'], ['T_MULT'], ['T_FACTOR']], lambda p, r, c: int(r[0][1]) * int(r[2][1])),
		  TokenSequence(None, [['T_FACTOR'], ['T_DIV'], ['T_FACTOR']], lambda p, r, c: int(r[0][1]) - int(r[2][1])),
		 ], ReturnDirect))

A(CompositeToken('T_ADDITIVE_EXPR',
		 [TokenSequence(None, [['T_TERM'], ['T_ADD'], ['T_TERM']], lambda p, r, c: int(r[0][1]) + int(r[2][1])),
		  TokenSequence(None, [['T_TERM'], ['T_SUB'], ['T_TERM']], lambda p, r, c: int(r[0][1]) - int(r[2][1])),
		 ], ReturnDirect))

print parser.scan(['T_EXPR'])
