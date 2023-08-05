# ZestyParser 0.4.1 -- Parses in Python zestily
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

__all__ = ('ZestyParser', 'NotMatched', 'ParseError', 'EOF', 'ReturnRaw', 'AbstractToken', 'Token', 'RawToken', 'CompositeToken', 'TokenSequence', 'CallbackFor')

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

class Token (AbstractToken):
	def __init__(self, regex, callback=None, name=None):
		self.name, self.regex, self.callback = name, regex, callback
		if not hasattr(regex, 'match'):
			self.regex = re.compile(self.regex, re.DOTALL)
	
	def __call__(self, parser, origCursor):
		matches = self.regex.match(parser.data, origCursor)
		if not matches: raise NotMatched

		#parser.cursor += len(matches.group())
		parser.cursor = matches.end()
		return self.preprocessResult(parser, matches, origCursor)
	
	def __str__(self):
		return self.regex.pattern

class RawToken (AbstractToken):
	def __init__(self, string, callback=None, name=None):
		self.string, self.callback, self.name = string, callback, name
		self.len = len(self.string)
	
	def __call__(self, parser, origCursor):
		if parser.data[origCursor:origCursor+self.len] == self.string:
			parser.cursor += self.len
			return self.preprocessResult(parser, self.string, origCursor)
		else:
			raise NotMatched
	
	def __str__(self):
		return repr(self.string)

class CompositeToken (AbstractToken):
	def __init__(self, tokens, callback=None, name=None):
		self.name = name
		self.tokens = tokens
		self.callback = callback
	
	def __call__(self, parser, origCursor):
		r = parser.scan(self.tokens)
		if not r or parser.last is EOF:
			raise NotMatched
		return self.preprocessResult(parser, r, origCursor)
	
	def __str__(self):
		return '(' + ' | '.join([str(t) for t in self.tokens]) + ')'
	
	def __or__(self, other):
		if isinstance(other, CompositeToken):
			return CompositeToken(self.tokens + other.tokens)
		else:
			return CompositeToken(self.tokens + [other])

class TokenSequence (AbstractToken):
	def __init__(self, tokenGroups, callback=None, name=None):
		self.name = name
		self.tokenGroups = tokenGroups
		self.callback = callback
	
	def __call__(self, parser, origCursor):
		o = []
		for g in self.tokenGroups:
			r = parser.scan(g)
			if not r:
				parser.cursor = origCursor
				raise NotMatched
			o.append(r)
		return self.preprocessResult(parser, o, origCursor)
	
	def __str__(self):
		return '(' + ' + '.join([str(t) for t in self.tokenGroups]) + ')'

	def __add__(self, other):
		if isinstance(other, TokenSequence):
			return TokenSequence(self.tokenGroups + other.tokenGroups)
		else:
			return TokenSequence(self.tokenGroups + [other])

class ZestyParser:
	tokens = {}
	data = None
	cursor = 0

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
			except NotMatched:
				self.cursor = oldCursor
				continue
			self.last = t
			return r
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
			return False
		return True

	def scanMultiple(self, *tokenGroups):
		return self.scan([TokenSequence(tokenGroups)])
	
	def take(self, num):
		r = self.data[self.cursor:self.cursor+num]
		self.cursor += num
		return r
	
	def iter(self, tokens): return ParserIterator(tokens, self)
	
	def coord(self, loc=None):
		if not loc: loc = self.cursor
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
		if not r:
			raise StopIteration
		return r
