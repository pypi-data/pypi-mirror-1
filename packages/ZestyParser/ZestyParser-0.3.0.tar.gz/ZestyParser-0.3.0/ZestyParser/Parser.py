# ZestyParser 0.3.0 -- Parses in Python zestily
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

import re

class Error(Exception): pass
class NotMatched(Error): pass
class ParseError(Error):
	def __init__(self, parser, message):
		self.parser, self.message, self.coord = parser, message, parser.coord()
	def __str__(self):
		return "%s at line %i column %i" % (self.message, self.coord[0], self.coord[1])

def EOF(parser, origCursor):
	if parser.cursor != parser.len: raise NotMatched

def ReturnRaw(parser, matches, cursor): return matches.group()
def ReturnDirect(parser, result, cursor): return result[1]

class AbstractToken:
	def __repr__(self):
		return '%s %s' % (self.__class__.__name__, (self.name or 'None'))
	def preprocessResult(self, parser, data, origCursor):
		if self.callback is None:
			return data
		try:
			return self.callback(parser, data, origCursor)
		except NotMatched:
			parser.cursor = origCursor
			raise NotMatched

class Token (AbstractToken):
	def __init__(self, tokenName, regex, callback=None):
		self.name, self.regex, self.callback = tokenName, regex, callback
		if not hasattr(regex, 'match'):
			self.regex = re.compile(self.regex, re.DOTALL)
	
	def __call__(self, parser, origCursor):
		matches = self.regex.match(parser.data, origCursor)
		if matches is None: raise NotMatched

		parser.cursor += len(matches.group())
		return self.preprocessResult(parser, matches, origCursor)

class CompositeToken (AbstractToken):
	def __init__(self, tokenName, tokens, callback=None):
		self.name = tokenName
		self.tokens = tokens
		self.callback = callback
	
	def __call__(self, parser, origCursor):
		r = parser.scan(self.tokens)
		if not r or r[0] is EOF:
			raise NotMatched
		return self.preprocessResult(parser, r, origCursor)

class TokenSequence (AbstractToken):
	def __init__(self, tokenName, tokenGroups, callback=None):
		self.name = tokenName
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

class ZestyParser:
	tokens = {}
	data = None

	def __init__(self, data=None):
		if data: self.useData(data)

	def useData(self, data):
		self.data = data
		self.cursor = 0
		self.len = len(data)
	
	def addTokens(self, *tokens):
		for t in tokens:
			self.tokens[t.name] = t

	def scan(self, tokens):
		for t in tokens:
			if t.__class__ is str:
				t = self.tokens[t]

			oldCursor = self.cursor
			try:
				return (t, t(self, oldCursor))
			except NotMatched:
				self.cursor = oldCursor
				continue

		return None

	def scanMultiple(self, *tokenGroups):
		r = self.scan([TokenSequence(None, tokenGroups)])
		if r: return r[1]
	
	def take(self, num):
		r = self.data[self.cursor:self.cursor+num]
		self.cursor += num
		return r
	
	def iter(self, tokens): return ParserIterator(tokens, self)
	
	def coord(self):
		row = self.data.count('\n', 0, self.cursor)
		col = self.cursor - self.data.rfind('\n', 0, self.cursor)
		return (row + 1, col)

class ParserIterator:
	def __init__(self, tokens, parser):
		self.tokens = tokens
		self.parser = parser
	
	def __iter__(self): return self
	
	def next(self):
		r = self.parser.scan(self.tokens)
		if r is None:
			raise StopIteration
		return r
