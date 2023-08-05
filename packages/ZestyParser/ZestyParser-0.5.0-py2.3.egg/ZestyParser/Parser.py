# ZestyParser 0.5.0 -- Parses in Python zestily
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

__all__ = ('ZestyParser', 'NotMatched', 'ParseError', 'EOF', 'ReturnRaw', 'CallbackFor')

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
	
	def iter(self, tokens, skip=None): return ParserIterator(tokens, self, skip)
	
	def coord(self, loc=None):
		if loc is None: loc = self.cursor
		row = self.data.count('\n', 0, loc)
		col = loc - self.data.rfind('\n', 0, loc)
		return (row + 1, col)

class ParserIterator:
	def __init__(self, tokens, parser, skip=None):
		self.tokens, self.parser, self.skip = tokens, parser, skip
	
	def __iter__(self): return self
	
	def next(self):
		if self.skip:
			self.parser.skip(self.skip)
		r = self.parser.scan(self.tokens)
		if self.parser.last is None:
			raise StopIteration
		return r
