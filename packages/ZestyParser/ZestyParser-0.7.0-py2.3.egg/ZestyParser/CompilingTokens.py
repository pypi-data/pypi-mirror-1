# ZestyParser 0.6.0 -- Parses in Python zestily
# Copyright (C) 2006-2007 Adam Atlas
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import re, copy
from Parser import NotMatched, ParseError
import Tokens

__all__ = ('CompilingToken', 'Token', 'RawToken', 'CompositeToken', 'TokenSequence', 'TakeToken', 'TokenSeries', 'EmptyToken', 'Default', 'Skip', 'Omit', 'Defer', 'EOF')

rstack = []

class CompilingBase:
	def __add__(self, other):
		return TokenSequence([self, other])	
	def __or__(self, other):
		return CompositeToken([self, other])

class CompilingToken (CompilingBase, Tokens.AbstractToken):
	code = None
	def __init__(self, desc, code, callback=None, as=None, name=None):
		Tokens.AbstractToken.__init__(self, desc, callback, as, name)
		self.code = code
	def __call__(self, parser, origCursor):
		if type(self.code) is str:
			x = {}
			exec ('def f(self, parser, origCursor):\n' + self.code) in globals(), x
			self.code = x['f']
		return self.preprocessResult(parser, self.code(self, parser, origCursor), origCursor)

class Token (CompilingBase, Tokens.Token): pass

class RawToken (CompilingToken, Tokens.RawToken):
	def __init__(self, string, callback=None, as=None, name=None, caseInsensitive=False):
		code = '''
 end = origCursor + %i
 d = parser.data[origCursor:end]
''' % len(string)
		if caseInsensitive:
			string = string.lower()
			code += '''
 if d.lower() == self.desc:
'''
		else:
			code += '''
 if d == self.desc:
'''
		code += '''
  parser.cursor = end
  return d
 else: raise NotMatched
'''

		CompilingToken.__init__(self, string, code, callback, as, name)

class CompositeToken (CompilingBase, Tokens.CompositeToken): pass

class TokenSequence (CompilingToken, Tokens.TokenSequence):
	def __init__(self, desc, callback=None, as=None, name=None):
		code = ' o = []; d = self.desc\n'
		for i, t in zip(range(len(desc)), desc):
			code += '''
 r = parser.scan(d[%i])
 if parser.last is None: raise NotMatched
''' % i
			if not isinstance(t, (Skip, Omit)):
				code += '''
 o.append(r)
'''
		code += ' return o'
		self.finalcode = code
		CompilingToken.__init__(self, desc, code, callback, as, name)

	def __add__(self, other):
		if isinstance(other, TokenSequence):
			return TokenSequence(self.desc + other.desc)
		elif hasattr(other, '__iter__'):
			return TokenSequence(self.desc + list(other))
		else:
			return TokenSequence(self.desc + [other])
	
	def __iadd__(self, other):
		if isinstance(other, TokenSequence):
			self.desc += other.desc
		elif hasattr(other, '__iter__'):
			self.desc += list(other)
		else:
			self.desc.append(other)
		return self

class TakeToken (CompilingBase, Tokens.TakeToken): pass
class TokenSeries (CompilingBase, Tokens.TokenSeries): pass
class Default (CompilingBase, Tokens.Default): pass
EmptyToken = Default('')
class Skip (CompilingBase, Tokens.Skip): pass
class Omit (CompilingBase, Tokens.Omit): pass
class Defer (CompilingBase, Tokens.Defer): pass
class _EOF (CompilingBase, Tokens._EOF): pass
EOF = _EOF(None)

#class TakeToken (AbstractToken):
#	'''
#	A class whose instances match and return a given number of characters from the parser's L{data<ZestyParser.data>}. Raises L{NotMatched} if not enough characters are left.
#	'''
#	
#	def __init__(self, length, callback=None, as=None, name=None):
#		AbstractToken.__init__(self, length, callback, as, name)
#	
#	def __call__(self, parser, start):
#		end = start + self.desc
#		if parser.len < end: raise NotMatched
#		parser.cursor = end
#		return parser.data[start:end]
#
#class TokenSeries (AbstractToken):
#	'''
#	A particularly versatile class whose instances match one token multiple times.
#	
#	The properties L{skip}, L{prefix}, L{postfix}, and L{delimiter} are optional tokens which add structure to the series. It can be represented, approximately in the idioms of L{TokenSequence}, as follows::
#	
#		[Skip(skip) + Omit(prefix) + desc + Omit(postfix)] + [Skip(skip) + Omit(delimiter) + Skip(skip) + Omit(prefix) + desc + Omit(postfix)] + ... + Skip(skip)
#	
#	Or, if there is no delimiter::
#	
#		[Skip(skip) + Omit(prefix) + desc + Omit(postfix)] + ... + Skip(skip)
#	
#	@ivar desc: The token to match.
#	@type desc: token
#	@ivar min: The minimum number of times L{desc} must match.
#	@type min: int
#	@ivar max: The maximum number of times L{desc} will try to match.
#	@type max: int
#	@ivar skip: An optional token to skip between matches.
#	@type skip: token
#	@ivar prefix: An optional token to require (but omit from the return value) before each instance of L{token}.
#	@type prefix: token
#	@ivar postfix: An optional token to require (but omit from the return value) after each instance of L{token}.
#	@type postfix: token
#	@ivar delimiter: An optional token to require (but omit from the return value) between each instance of L{token}.
#	@type delimiter: token
#	@ivar until: An optional 2-tuple whose first item is a token, and whose second item is either a message or False. The presence of this property indicates that the token in C{until[0]} must match at the end of the series. If this fails, then if C{until[1]} is a message, a ParseError will be raised with that message; if it is False, NotMatched will be raised.
#	'''
#	def __init__(self, token, min=0, max=False, skip=EmptyToken, prefix=EmptyToken, postfix=EmptyToken, delimiter=None, until=None, includeDelimiter=False, callback=None, as=None, name=None):
#		AbstractToken.__init__(self, token, callback, as, name)
#		self.min, self.max, self.skip, self.prefix, self.postfix, self.delimiter, self.until, self.includeDelimiter = min, max, skip, prefix, postfix, delimiter, until, includeDelimiter
#
#	def __call__(self, parser, origCursor):
#		o = []
#		i = 0
#		done = False
#		while (self.max is False or i != self.max):
#			if self.until and parser.skip(self.until[0]): done = True; break
#			parser.skip(self.skip)
#
#			c = parser.cursor
#			if i != 0 and self.delimiter is not None:
#				d = parser.scan(self.delimiter)
#				if parser.last is None: parser.cursor = c; break
#				parser.skip(self.skip)
#			if not parser.skip(self.prefix): parser.cursor = c; break
#			t = parser.scan(self.desc)
#			if parser.last is None: parser.cursor = c; break
#			if not parser.skip(self.postfix): parser.cursor = c; break
#			
#			if i != 0 and self.includeDelimiter: o.append(d)
#			o.append(t)
#			i += 1
#		if not done and self.until:
#			if self.until[1]: raise ParseError(parser, self.until[1])
#			else: raise NotMatched
#		if len(o) >= self.min:
#			return self.preprocessResult(parser, o, origCursor)
#		else:
#			raise NotMatched
#
#class Defer (AbstractToken):
#	'''
#	A token which takes a callable (generally a lambda) which takes no arguments and itself returns a token. A Defer instance, upon being called, will call this function, scan for the returned token, and return that return value. This is primarily intended to allow you to define tokens recursively; if you need to refer to a token that hasn't been defined yet, simply use C{Defer(lambda: T_SOME_TOKEN)}, where C{T_SOME_TOKEN} is the token's eventual name.
#	'''
#	
#	def __init__(self, func, callback=None, as=None, name=None):
#		AbstractToken.__init__(self, func, callback, as, name)
#	
#	def __call__(self, parser, origCursor):
#		t = parser.scan(self.desc())
#		if parser.last is None: raise NotMatched
#		return t
#
#class Skip (AbstractToken):
#	'''
#	See L{TokenSequence}.
#	'''
#	def __call__(self, parser, origCursor):
#		parser.skip(self.desc)
#
#class Omit(AbstractToken):
#	'''
#	See L{TokenSequence}.
#	'''
#	def __call__(self, parser, origCursor):
#		if not parser.skip(self.desc): raise NotMatched
#
#class _EOF(AbstractToken):
#	def __call__(self, parser, origCursor):
#		if parser.cursor != parser.len: raise NotMatched
#EOF = _EOF(None)
