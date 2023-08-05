# ZestyParser 0.5.1 -- Parses in Python zestily
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
from Parser import NotMatched, ParseError, EOF

__all__ = ('AbstractToken', 'Token', 'RawToken', 'CompositeToken', 'TokenSequence', 'TakeToken', 'TokenSeries', 'EmptyToken', 'Skip', 'Defer')

rstack = []

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
	def __init__(self, regex, callback=None, name=None, group=None):
		if not hasattr(regex, 'match'):
			regex = re.compile(regex, re.DOTALL)
		AbstractToken.__init__(self, regex, callback, name)
		self.group = group
	
	def __call__(self, parser, origCursor):
		matches = self.desc.match(parser.data, origCursor)
		if not matches: raise NotMatched

		parser.cursor = matches.end()
		if self.group is not None: matches = matches.group(self.group)
		return self.preprocessResult(parser, matches, origCursor)
	
	def __str__(self):
		return repr(self.desc.pattern)

class RawToken (AbstractToken):
	def __init__(self, string, callback=None, name=None, caseInsensitive=False):
		AbstractToken.__init__(self, string, callback, name)
		self.len = len(string)
		self.caseInsensitive = caseInsensitive
		if caseInsensitive:
			self.desc = self.desc.lower()
	
	def __call__(self, parser, origCursor):
		end = origCursor + self.len
		d = parser.data[origCursor:end]
		if self.caseInsensitive and d.lower() == self.desc:
			parser.cursor = end
			return self.preprocessResult(parser, d, origCursor)
		elif not self.caseInsensitive and d == self.desc:
			parser.cursor = end
			return self.preprocessResult(parser, d, origCursor)
		else:
			raise NotMatched
	
	def __str__(self):
		return repr(self.desc)

EmptyToken = RawToken('')

class CompositeToken (AbstractToken):
	def __init__(self, tokens=[], callback=None, name=None):
		AbstractToken.__init__(self, tokens, callback, name)

	def __call__(self, parser, origCursor):
		r = parser.scan(self.desc)
		if parser.last in (None, EOF):
			raise NotMatched
		return self.preprocessResult(parser, r, origCursor)
	
	def __str__(self):
		if self in rstack:
			return '...'
		else:
			rstack.append(self)
			d = '(' + ' | '.join([repr(t) for t in self.desc]) + ')'
			rstack.pop()
			return d
	
	def __or__(self, other):
		if isinstance(other, CompositeToken):
			return CompositeToken(self.desc + other.desc)
		elif hasattr(other, '__iter__'):
			return CompositeToken(self.desc + list(other))
		else:
			return CompositeToken(self.desc + [other])
	
	def __ior__(self, other):
		if isinstance(other, CompositeToken):
			self.desc += other.desc
		elif hasattr(other, '__iter__'):
			self.desc += list(other)
		else:
			self.desc.append(other)
		return self

class TokenSequence (AbstractToken):
	def __init__(self, tokenGroups=[], callback=None, name=None):
		AbstractToken.__init__(self, tokenGroups, callback, name)

	def __call__(self, parser, origCursor):
		o = []
		for g in self.desc:
			r = parser.scan(g)
			if parser.last is None: raise NotMatched
			if not isinstance(parser.last, Skip): o.append(r)
		return self.preprocessResult(parser, o, origCursor)
	
	def __str__(self):
		if self in rstack:
			return '...'
		else:
			rstack.append(self)
			d = '(' + ' + '.join([repr(t) for t in self.desc]) + ')'
			rstack.pop()
			return d

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

class TakeToken (AbstractToken):
	def __init__(self, length, callback=None, name=None):
		AbstractToken.__init__(self, length, callback, name)
	
	def __call__(self, parser, start):
		end = start + self.desc
		if parser.len < end: raise NotMatched
		parser.cursor = end
		return parser.data[start:end]

class TokenSeries (AbstractToken):
	def __init__(self, token, min=0, max=False, skip=EmptyToken, prefix=EmptyToken, postfix=EmptyToken, delimiter=EmptyToken, until=None, callback=None, name=None):
		AbstractToken.__init__(self, token, callback, name)
		self.min, self.max, self.skip, self.prefix, self.postfix, self.delimiter, self.until = min, max, skip, prefix, postfix, delimiter, until
		self.scanFor = TokenSequence([Skip(skip), prefix, token, postfix], lambda r: r[1])
		self.scanForSecondary = TokenSequence([Skip(skip), delimiter, Skip(skip), prefix, token, postfix], lambda r: r[2])

	def __call__(self, parser, origCursor):
		o = []
		i = 0
		while (self.max is False or i != self.max):
			parser.skip(self.skip)
			if self.until and parser.skip(self.until[0]): break
			
			if i == 0: d = self.scanFor
			else: d = self.scanForSecondary
			t = parser.scan(d)
			if parser.last is None:
				if self.until:
					if self.until[1]: raise ParseError(parser, self.until[1])
					else: raise NotMatched
				else: break
			o.append(t)
			i += 1
		if len(o) >= self.min:
			return self.preprocessResult(parser, o, origCursor)
		else:
			raise NotMatched

class Defer (AbstractToken):
	def __init__(self, func, callback=None, name=None):
		AbstractToken.__init__(self, func, callback, name)
	
	def __call__(self, parser, origCursor):
		t = parser.scan(self.desc())
		if parser.last is None: raise NotMatched
		return t

class Skip (AbstractToken):
	def __init__(self, token, callback=None, name=None):
		AbstractToken.__init__(self, token, callback, name)
	
	def __call__(self, parser, origCursor):
		parser.skip(self.desc)