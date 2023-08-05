# ZestyParser 0.4.2 -- Parses in Python zestily
# Copyright (C) 2006 Adam Atlas
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

__all__ = ('ZestyParser', 'NotMatched', 'ParseError', 'EOF', 'ReturnRaw', 'AbstractToken', 'Token', 'RawToken', 'CompositeToken', 'TokenSequence', 'TakeToken', 'CallbackFor')

class Error(Exception): pass
class NotMatched(Error): pass
class ParseError(Error):
	def __init__(self, parser, message):
		self.parser, self.message, self.coord = parser, message, parser.coord()
	def __str__(self):
		return "%s at line %i column %i" % (self.message, self.coord[0], self.coord[1])

def EOF(parser, origCursor):
	if parser.cursor != parser.len: raise NotMatched

def ReturnRaw(matches): return matches.group()

class CallbackFor:
	def __init__(self, token):
		self.token = token
	
	def __call__(self, func):
		self.token.callback = func
		return self.token

class AbstractToken:
	def __init__(self, desc, callback=None, name=None):
		self.desc, self.callback, self.name, self.failMessage = desc, callback, name, None
	
	def __repr__(self):
		return '%s %s' % (self.__class__.__name__, (self.name or str(self)))
	
	def preprocessResult(self, parser, data, origCursor):
		if not self.callback:
			return data
		try:
			c = self.callback.func_code.co_argcount
			if c == 2: return self.callback(parser, data)
			elif c == 1: return self.callback(data)
			else: return self.callback(parser, data, origCursor)
		except NotMatched:
			parser.cursor = origCursor
			raise NotMatched

	def __add__(self, other):
		return TokenSequence([self, other])
	
	def __or__(self, other):
		return CompositeToken([self, other])
	
	def __rshift__(self, callback):
		new = copy.copy(self)
		new.callback = callback
		return new
	
	def __xor__(self, message):
		new = copy.copy(self)
		new.failMessage = message
		return new

class Token (AbstractToken):
	def __init__(self, regex, callback=None, name=None):
		if not hasattr(regex, 'match'):
			regex = re.compile(regex, re.DOTALL)
		AbstractToken.__init__(self, regex, callback, name)
	
	def __call__(self, parser, origCursor):
		matches = self.desc.match(parser.data, origCursor)
		if not matches: raise NotMatched

		#parser.cursor += len(matches.group())
		parser.cursor = matches.end()
		return self.preprocessResult(parser, matches, origCursor)
	
	def __str__(self):
		return self.desc.pattern

class RawToken (AbstractToken):
	def __init__(self, string, callback=None, name=None):
		AbstractToken.__init__(self, string, callback, name)
		self.len = len(string)
	
	def __call__(self, parser, origCursor):
		if parser.data[origCursor:origCursor+self.len] == self.desc:
			parser.cursor += self.len
			return self.preprocessResult(parser, self.desc, origCursor)
		else:
			raise NotMatched
	
	def __str__(self):
		return repr(self.desc)

class CompositeToken (AbstractToken):
	def __init__(self, tokens, callback=None, name=None):
		AbstractToken.__init__(self, tokens, callback, name)

	def __call__(self, parser, origCursor):
		r = parser.scan(self.desc)
		if parser.last in (None, EOF):
			raise NotMatched
		return self.preprocessResult(parser, r, origCursor)
	
	def __str__(self):
		return '(' + ' | '.join([str(t) for t in self.desc]) + ')'
	
	def __or__(self, other):
		if isinstance(other, CompositeToken):
			return CompositeToken(self.desc + other.desc)
		else:
			return CompositeToken(self.desc + [other])

class TokenSequence (AbstractToken):
	def __init__(self, tokenGroups, callback=None, name=None):
		AbstractToken.__init__(self, tokenGroups, callback, name)

	def __call__(self, parser, origCursor):
		o = []
		for g in self.desc:
			r = parser.scan(g)
			if parser.last is None:
				parser.cursor = origCursor
				raise NotMatched
			o.append(r)
		return self.preprocessResult(parser, o, origCursor)
	
	def __str__(self):
		return '(' + ' + '.join([str(t) for t in self.desc]) + ')'

	def __add__(self, other):
		if isinstance(other, TokenSequence):
			return TokenSequence(self.desc + other.desc)
		else:
			return TokenSequence(self.desc + [other])

class TakeToken (AbstractToken):
	def __init__(self, length, callback=None, name=None):
		AbstractToken.__init__(self, length, callback, name)
	
	def __call__(self, parser, start):
		end = start + self.desc
		if parser.len < end: raise NotMatched
		parser.cursor = end
		return parser.data[start:end]

class ZestyParser:
	tokens = {}
	data = None
	cursor = 0
	len = 0

	def __init__(self, data=None):
		if data: self.useData(data)
		self.last = None

	def useData(self, data):
		self.data = data
		self.cursor = 0
		self.len = len(data)
	
	def addTokens(self, *tokens, **moreTokens):
		for t in tokens:
			self.tokens[t.name] = t
		for n in moreTokens:
			self.tokens[n] = moreTokens[n]

	def scan(self, tokens):
		if not hasattr(tokens, '__iter__'):
			tokens = (tokens,)
		for t in tokens:
			if t.__class__ is str:
				t = self.tokens[t]

			oldCursor = self.cursor
			try:
				r = t(self, oldCursor)
				self.last = t
				return r
			except NotMatched:
				self.cursor = oldCursor
				if hasattr(t, 'failMessage') and t.failMessage: raise ParseError(self, t.failMessage)
		self.last = None
		return None
	
	def skip(self, t):
		if t.__class__ is str:
			t = self.tokens[t]
		oldCursor = self.cursor
		try:
			t(self, oldCursor)
		except NotMatched:
			self.cursor = oldCursor
			if hasattr(t, 'failMessage') and t.failMessage: raise ParseError(self, t.failMessage)
			else: return False
		return True
	
	def iter(self, tokens): return ParserIterator(tokens, self)
	
	def coord(self, loc=None):
		if loc is None: loc = self.cursor
		row = self.data.count('\n', 0, loc)
		col = loc - self.data.rfind('\n', 0, loc)
		return (row + 1, col)

class ParserIterator:
	def __init__(self, tokens, parser):
		self.tokens = tokens
		self.parser = parser
	
	def __iter__(self): return self
	
	def next(self):
		r = self.parser.scan(self.tokens)
		if self.parser.last is None:
			raise StopIteration
		return r
