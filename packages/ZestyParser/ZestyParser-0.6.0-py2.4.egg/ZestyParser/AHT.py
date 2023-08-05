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

'''
@version: 0.6.0
@author: Adam Atlas
@copyright: Copyright 2006-2007 Adam Atlas. Released under the terms of the GNU General Public License.
@contact: adam@atlas.st

AHT (Ad Hoc Types) is a utility module providing an easy way to generate "labels" for objects in abstract parse trees without defining a class for each one.

To use it, create an instance of L{Env}. Now you can access any property on it and get a unique type for that name. The first time such a type is called, it becomes a subclass of the type of whatever it is passed. For example, C{EnvInstance.SomeEntity("hi")} marks C{SomeEntity} as being a subclass of C{str}, and returns an instance of itself initialized with C{"hi"}.) Now you can check at any time with nothing more than a C{isinstance(something, EnvInstance.SomeEntity)} how a piece of data was instantiated.

Ad Hoc Types are primarily intended to be used in conjunction with L{AbstractToken} types, where you should set it as the C{as} parameter, or, if it is more convenient (e.g. when you must use C{>>}), as its callback.
'''

from types import ClassType

__all__ = ('Env',)

class Env:
	'''
	@see: L{AHT}
	'''
	_aht_types = {}
	
	def __getattr__(self, attr):
		if attr in self._aht_types:
			return self._aht_types[attr]
		else:
			return _AHTFactory(self, attr)

class _AHTFactory:
	def __init__(self, env, name):
		self.env, self.name = env, name
	
	def __call__(self, arg):
		if self.name not in self.env._aht_types:
			self.env._aht_types[self.name] = ClassType(self.name, (arg.__class__,), {})
		return self.env._aht_types[self.name](arg)