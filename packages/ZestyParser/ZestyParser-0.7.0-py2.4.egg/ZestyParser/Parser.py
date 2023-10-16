# ZestyParser 0.7.0 -- Parses in Python zestily
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

'''
@version: 0.7.0
@author: Adam Atlas
@copyright: Copyright 2006-2007 Adam Atlas. Released under the terms of the GNU General Public License.
@contact: adam@atlas.st
'''

__all__ = ('ZestyParser', 'NotMatched', 'ParseError', 'CallbackFor', 'DebugNote')

class Error(Exception): pass
class NotMatched(Error): '''Raised by a token if it has failed to match at the parser's current cursor.'''
class ParseError(Error):
	'''Raised by a token to indicate that a parse error has occurred.'''
	def __init__(self, parser, message):
		'''
		@param parser: The parser instance that encountered the error.
		@type parser: ZestyParser
		@param message: A message explaining the error.
		@type message: str
		'''
		self.parser, self.message, self.coord = parser, message, parser.coord()
	def __str__(self):
		'''Prints the error message and the row and column corresponding to the parser's cursor.'''
		return "%s at line %i column %i" % (self.message, self.coord[0], self.coord[1])

def CallbackFor(token):
	'''
	Function decorator indicating that the function should be set as the callback of the given token; returns the token instead of the function.
	
	Example::
		@CallbackFor(Token('([0-9]+)'))
		def T_INT(r):
			print r
	
	This is equivalent to::
		def T_INT(r):
			print r
		T_INT = Token('([0-9]+)', callback=T_INT)
	'''
	def newFunc(func):
		return token >> func
	return newFunc

def DebugNote(note):
	'''
	Factory which creates a logging function usable as a token callback. The logging function prints L{note}, the parser's coordinates, and the value matched. It then returns the value unmodified.
	
	Example::
		T_FOO = TokenSeries(RawToken('foo')) >> DebugNote('foo_series')
	'''
	def func(parser, val, cursor):
		coord = parser.coord()
		print '%s(%i, %i): %s' % (note, coord[0], coord[1], val)
		return val
	return func

class ZestyParser:
	'''
	Parses one stream of data, by means of L{tokens<ZestyParser.Tokens>}.
	
	@ivar context: A dictionary which can be used for storing any necessary state information.
	@type context: dict
	@ivar data: The sequence being parsed (probably a string).
	@type data: sequence
	@ivar cursor: The current position of the parser in L{data}.
	@type cursor: int
	@ivar last: The last matched token.
	@type last: L{token<ZestyParser.Tokens>}
	'''
	
	context = {}
	data = None
	cursor = 0
	len = 0
	last = None

	def __init__(self, data=None):
		'''Initializes the parser, optionally calling L{useData}'''
		if data: self.useData(data)
		self.last = None

	def useData(self, data):
		'''
		Begin parsing a stream of data
		
		@param data: The data to parse.
		@type data: sequence
		'''
		self.data = data
		self.cursor = 0
		self.len = len(data)
	
	def scan(self, token):
		'''
		Scan for one token.
		
		@param token: The token to scan for.
		@return: The return value of the matching token, or None if the token raised NotMatched.
		@rtype: object
		@raise ParseError: If a token fails to match and it has a failMessage parameter.
		'''
		oldCursor = self.cursor
		try:
			r = token(self, oldCursor)
			self.last = token
			return r
		except NotMatched:
			self.cursor = oldCursor
			self.last = None
			return None
	
	def skip(self, token):
		'''
		A convenience method that skips one token and returns whether it matched.
		
		@param token: The token to scan for.
		@type token: token
		@return: Whether or not the token matched.
		@rtype: bool
		'''
		oldCursor = self.cursor
		try:
			token(self, oldCursor)
		except NotMatched:
			self.cursor = oldCursor
			return False
		return True
	
	def iter(self, token, skip=None, until=None):
		'''
		Returns a generator iterator which scans for L{token} every time it is invoked.
		
		@param token: The token to scan for.
		@param skip: An optional token to L{skip} before each L{scan} for L{token}.
		@type skip: token
		@param until: An optional 2-tuple. If defined, the iterator will scan for L{token} until it reaches the token C{until[0]}; if L{scan} returns C{None} before the iterator encounters this token, it raises a L{ParseError} with the message given in C{until[1]}.
		@type until: tuple
		@rtype: iterator
		'''
		while 1:
			if skip: self.skip(skip)
			if until and self.skip(until[0]): break
			r = self.scan(token)
			if self.last: yield r
			else:
				if until: raise ParseError(self, until[1])
				else: break
	
	def coord(self, loc=None):
		'''
		Returns row/column coordinates for a given point in the input stream, or L{cursor} by default. Counting starts at C{(1, 1)}.
		
		@param loc: An index of L{data}.
		@type loc: int
		@return: A 2-tuple representing (row, column).
		@rtype: tuple
		'''
		if loc is None: loc = self.cursor
		row = self.data.count('\n', 0, loc) + 1
		col = loc - self.data.rfind('\n', 0, loc)
		return (row, col)