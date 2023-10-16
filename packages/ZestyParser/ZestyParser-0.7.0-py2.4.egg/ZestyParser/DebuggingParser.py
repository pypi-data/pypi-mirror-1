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

import Parser, sys

#todo - configurable levels of verbosity?
#use `logging` stdlib module?

class DebuggingParser(Parser.ZestyParser):
    '''
    A L{Parser.ZestyParser} subclass which is useful for debugging parsers. It parses as usual, but it also prints a comprehensive trace to stderr.
    '''
    depth = -1
    
    def scan(self, token):
        self.depth += 1
        ind = ' |  ' * self.depth
        
        print >> sys.stderr, '%sBeginning to scan for %r at position %i' % (ind, token, self.cursor)
        r = Parser.ZestyParser.scan(self, token)
        
        if self.last:
            print >> sys.stderr, '%sGot %r -- now at %i' % (ind, r, self.cursor)
        else:
            print >> sys.stderr, "%sDidn't match" % (ind)
        
        self.depth -= 1
        
        return r
    
    def skip(self, token):
        self.depth += 1
        ind = ' |  ' * self.depth
        
        print >> sys.stderr, '%sBeginning to skip %r at position %i' % (ind, token, self.cursor)
        r = Parser.ZestyParser.skip(self, token)
        
        if r:
            print >> sys.stderr, '%sMatched -- now at %i' % (ind, self.cursor)
        else:
            print >> sys.stderr, "%sDidn't match" % (ind)
        
        self.depth -= 1
        
        return r
    
    def iter(self, token, *args, **kwargs):
        self.depth += 1
        ind = ' |  ' * self.depth
        
        print >> sys.stderr, '%sBeginning to iterate %r at position %i' % (ind, token, self.cursor)
        
        i = Parser.ZestyParser.iter(self, token, *args, **kwargs)
        while 1:
            print >> sys.stderr, '%sIterating' % ind
            yield i.next()
        
        print >> sys.stderr, '%sDone iterating -- now at %i' % (ind, self.cursor)

        self.depth -= 1