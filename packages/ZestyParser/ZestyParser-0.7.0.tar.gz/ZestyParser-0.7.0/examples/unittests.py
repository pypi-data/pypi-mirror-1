from ZestyParser import *

p = ZestyParser()
def sc(data, fail=False):
    p.useData(data)
    return p.scan(t)

def success(data):
    p.useData(data)
    p.scan(t)
    return p.last
def fail(data):
    return not success(data)

t = Token('[abc]+')
assert sc('abcbaacaqxz').group(0) == 'abcbaaca'

t = Token('(a)(b)', group=2)
assert sc('ab') == 'b'

t = RawToken('abc')
assert sc('abcde') == 'abc'

t = Default('beep')
assert sc('123') == 'beep' and p.cursor == 0

t = CompositeToken([RawToken('abc'), RawToken('def')])
assert sc('abcd') == 'abc'
assert sc('defg') == 'def'

t = TokenSequence([RawToken('abc'), RawToken('def')])
assert sc('abcdef') == ['abc', 'def']

t = TokenSequence([RawToken('abc'), Omit(RawToken('xyz')), RawToken('def')])
assert fail('abcdef')
assert sc('abcxyzdef') == ['abc', 'def']

t = TokenSequence([RawToken('abc'), Skip(RawToken('xyz')), RawToken('def')])
assert sc('abcdef') == ['abc', 'def']
assert sc('abcxyzdef') == ['abc', 'def']

t = TokenSequence([RawToken('abc'), Only(RawToken('xyz')), RawToken('def')])
assert fail('abcdef')
assert fail('abcxyz')
assert sc('abcxyzdef') == 'xyz'

t = Skip(RawToken(' ')).pad(TokenSequence([RawToken('abc'), RawToken('def')]))
assert sc('abcdef') == ['abc', 'def']
assert sc('abc def') == ['abc', 'def']

t = TakeToken(3)
assert sc('abc') == 'abc'

t = TokenSeries(RawToken('abc'))
assert sc('abcabcabc') == ['abc', 'abc', 'abc']
assert sc('') == []

t = TokenSeries(RawToken('abc'), min=3)
assert sc('abcabc') is None and p.last is None
assert sc('abcabcabc') == ['abc', 'abc', 'abc']

t = TokenSeries(RawToken('abc'), max=3)
assert sc('abcabcabcabc') == ['abc', 'abc', 'abc']

t = TokenSeries(RawToken('abc'), skip=RawToken('X'))
assert sc('abcabcabc') == ['abc', 'abc', 'abc']
assert sc('abcabcXabcabcXabc') == ['abc', 'abc', 'abc', 'abc', 'abc']

t = TokenSeries(RawToken('abc'), min=1, prefix=RawToken('X'))
assert sc('abcabcabc') is None and p.last is None
assert sc('XabcXabcXabc') == ['abc', 'abc', 'abc']

t = TokenSeries(RawToken('abc'), min=1, postfix=RawToken('X'))
assert sc('abcabcabc') is None and p.last is None
assert sc('abcXabcXabcX') == ['abc', 'abc', 'abc']

t = TokenSeries(RawToken('abc'), delimiter=RawToken('|'))
assert sc('abcabcabc') == ['abc']
assert sc('abc|abc|abc') == ['abc', 'abc', 'abc']

t = TokenSeries(RawToken('abc'), delimiter=RawToken('|'), includeDelimiter=True)
assert sc('abc|abc|abc|') == ['abc', '|', 'abc', '|', 'abc']

t = TokenSeries(RawToken('abc'), until=(RawToken('def'), 'ALAS'))
assert sc('abcabcabcdef') == ['abc', 'abc', 'abc']
try:
    assert not sc('abcabcabc')
except ParseError:
    pass

t = TokenSeries(RawToken('abc'), until=(RawToken('def'), None))
assert sc('abcabcabcdef') == ['abc', 'abc', 'abc']
assert sc('abcabcabc') is None and p.last is None

t = Defer(lambda:x)
x = RawToken('abc')
assert sc('abc') == 'abc'

t = Lookahead(RawToken('abc'))
assert sc('abc') == 'abc' and p.cursor == 0

t = Negative(RawToken('abc'))
assert sc('def') is True and p.cursor == 0

t = EOF
assert sc('') is None