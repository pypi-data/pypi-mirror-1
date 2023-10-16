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
@group Basic Tokens: RawToken,Token,TakeToken
@group Complex Tokens: CompositeToken,TokenSequence,TokenSeries
@group Special Tokens: Defer,Default,Lookahead,Negative
@group TokenSequence Flags: Omit,Skip,Only

@version: 0.7.0
@author: Adam Atlas
@copyright: Copyright 2006-2007 Adam Atlas. Released under the terms of the GNU General Public License.
@contact: adam@atlas.st

@var EmptyToken: A L{Default} instance initialized with the empty string.
@var EOF: A token which matches (and returns C{None}) if the parser is at the end of its L{data <ZestyParser.data>} sequence.

In ZestyParser, a token object must, at minimum, be a callable taking a L{ZestyParser <Parser.ZestyParser>} instance and its current L{cursor <ZestyParser.cursor>} as parameters. It can do whatever it needs with the parser's L{data <ZestyParser.data>} and L{cursor <ZestyParser.cursor>} properties before returning. It may raise L{NotMatched} to indicate to the L{ZestyParser <Parser.ZestyParser>} instance that it failed to match; it may also raise L{ParseError} to indicate, for instance, that it began matching successfully but encountered an unrecoverable error.

The L{Tokens} module contains a variety of predefined token classes (instances of which are callable) and other valid token objects which should cover most parsing situations.
'''

import re, copy, sys, types, new
from Parser import NotMatched, ParseError

__all__ = ('AbstractToken', 'TokenWrapper', 'Token', 'RawToken', 'CompositeToken', 'TokenSequence', 'TakeToken', 'TokenSeries', 'EmptyToken', 'Default', 'Skip', 'Omit', 'Only', 'Defer', 'Lookahead', 'Negative', 'EOF', 'Const')

rstack = []

def count_args(callable):
    t = type(callable)
    if t in (types.TypeType, types.BuiltinFunctionType):
        #builtin methods don't provide argcounts, so the best we can do is assume they only take the data itself as a parameter
        return 1
    elif t is types.FunctionType:
        return callable.func_code.co_argcount
    elif t is types.ClassType:
        return callable.__init__.im_func.func_code.co_argcount - 1
    elif t is types.InstanceType:
        return callable.__call__.im_func.func_code.co_argcount - 1
    elif t is types.MethodType:
        return callable.im_func.func_code.co_argcount - 1

class AbstractToken:
    '''
    Base class from which most tokens defined in this module derive. Subclassing this is not required for writing tokens, since they can be any callable with certain semantics, but this class provides several useful services for creating reusable token classes, such as callback support and convenient operator overloading.
    
    @ivar desc: The generic "description" variable which stores the "essence" of any given instance. Subclasses use this as needed.
    @ivar callback: An optional callable which, if not None, will be called whenever an instance matches successfully. It may take one, two, or three parameters, depending on its needs. If one, it will be passed whatever data the token matched (i.e. whatever it would normally have returned upon being called). If two, it will be passed the L{ZestyParser <Parser.ZestyParser>} instance and the data. If three, it will be passed the parser, the data, and the what the parser's cursor was when this token started matching. Callbacks may raise L{NotMatched} or L{ParseError} with the usual behaviour. They should also return a value, which will be returned to the calling L{ZestyParser <Parser.ZestyParser>} instance.
    @ivar to: An optional callable which, if not None, will be called in the same manner as a callback (after any callback and before returning to the parser instance), but will be passed only one argument: the data matched (or returned by the callback, if any). Its main purpose is to allow you to concisely do things like C{Token('[0-9]+', group=0, to=int)} -- the builtin callable C{int} will be passed the text matched by the regex, so the token will ultimately return an integer instead of a string or a regex match object. You can also use this property with L{AHT} types, for more complex multi-stage parsing. See the C{n3.py} and C{n3rdflib.py} examples for a demonstration of this. (In previous versions, this was passed to the initializer as C{as}, but this is deprecated because C{as} will become a reserved word in Python 2.6. Change your code to use {to}.)
    '''
    
    failMessage = None
    callbackArgCount = False
    _call_orig = None
    callback = None
    to = None

    #'as' is deprecated in favor of 'to' since it's becoming a reserved word
    def __init__(self, desc, callback=None, to=None, as=None, name=None):
        self._call_orig = self.__call__
        self.desc = desc
        self.callback = callback
        self.to = self.as = to or as
        self.name = name
    
    def __repr__(self):
        return '%s %s' % (self.__class__.__name__, (self.name or str(self)))

    def __str__(self): return ''

    def _call_preprocess(self, parser, origCursor):
        data = self._call_orig(parser, origCursor)
        if self.callback is not None:
            if self.callbackArgCount == 2:
                data = self.callback(parser, data)
            elif self.callbackArgCount == 1:
                data = self.callback(data)
            elif self.callbackArgCount == 3:
                data = self.callback(parser, data, origCursor)
        if self.to is not None: data = self.to(data)
        return data
    
    def _call_failcheck(self, parser, origCursor):
        try:
            data = self._call_preprocess(parser, origCursor)
            return data
        except NotMatched:
            if self.failMessage: raise ParseError(parser, self.failMessage)
            else: raise
        
    def __copy__(self):
        n = new.instance(self.__class__)
        n.__dict__.update(self.__dict__)
        if '__call__' in n.__dict__:
            del n.__call__
        n._call_orig = n.__call__
        return n

    def __add__(self, other):
        '''Allows you to construct L{TokenSequence}s with the + operator.'''
        return TokenSequence([self, other])
    
    def __or__(self, other):
        '''Allows you to construct L{CompositeToken}s with the | operator.'''
        return CompositeToken([self, other])
    
    def __rshift__(self, callback):
        '''
        Convenience overloading for setting the L{callback<AbstractToken.callback>} of a token whose initializer you do not call directly, such as the result of combining tokens with L{+<__add__>} or L{|<__or__>}.
        
        @param callback: An L{AbstractToken}-compatible callback.
        @type callback: callable
        @return: A copy of C{self} with the L{callback<AbstractToken.callback>} property set to C{callback}.
        '''
        new = copy.copy(self)
        new.callback = callback
        return new
    
    def __xor__(self, message):
        '''
        Overloading for setting the L{failMessage<AbstractToken.failMessage>} of a token.
        
        @param message: The message to be raised with L{ParseError} if this token fails to match.
        @type message: str
        @return: A copy of C{self} with the L{failMessage<AbstractToken.failMessage>} property set to C{callback}.
        '''
        new = copy.copy(self)
        new.failMessage = message
        return new
    
    def __invert__(self):
        return Negative(self)
    
    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name in ('callback', 'failMessage', 'to'):
            if self.failMessage:
                self.__call__ = self._call_failcheck
            elif self.callback or self.to:
                self.__call__ = self._call_preprocess
            else:
                self.__call__ = self._call_orig
        if name == 'callback':
            self.callbackArgCount = count_args(value)

class TokenWrapper (AbstractToken):
    '''If you write your own token type in a way other than subclassing AbstractToken, e.g. by simply writing a function, you can use this as a decorator to automatically let it take advantage of AbstractToken's magic.
    '''
    def __call__(self, parser, origCursor):
        return self.desc(parser, origCursor)

    def __str__(self):
        return repr(self.desc)

class Token (AbstractToken):
    '''
    A class whose instances match Python regular expressions.
    
    @ivar group: If defined, L{__call__} returns that group of the regular expression match instead of the whole match object.
    @type group: int
    '''
    
    def __init__(self, regex, group=None, **kwargs):
        '''
        @param regex: Either a compiled regex object or a string regex.
        @param group: To be set as the object's L{group} property.
        @type group: int
        '''
        if not hasattr(regex, 'match'):
            regex = re.compile(regex, re.DOTALL)
        AbstractToken.__init__(self, regex, **kwargs)
        self.group = group
    
    def __call__(self, parser, origCursor):
        matches = self.desc.match(parser.data, origCursor)
        if matches is None: raise NotMatched

        parser.cursor = matches.end()
        if self.group is not None: matches = matches.group(self.group)
        return matches
    
    def __str__(self):
        return repr(self.desc.pattern)

class RawToken (AbstractToken):
    '''
    A class whose instances match only a particular string. Returns that string.
    
    @ivar caseInsensitive: If true, ignores case.
    @type caseInsensitive: bool
    '''
    def __init__(self, string, caseInsensitive=False, **kwargs):
        '''
        @param string: The string to match.
        @type string: str
        @param caseInsensitive: To be set as the object's L{caseInsensitive} property.
        @type caseInsensitive: bool
        '''
        AbstractToken.__init__(self, string, **kwargs)
        self.len = len(string)
        self.caseInsensitive = caseInsensitive
        if caseInsensitive:
            self.desc = self.desc.lower()
    
    def __call__(self, parser, origCursor):
        end = origCursor + self.len
        d = parser.data[origCursor:end]
        if (not self.caseInsensitive and d == self.desc) or (self.caseInsensitive and d.lower() == self.desc):
            parser.cursor = end
            return d
        else: raise NotMatched
    
    def __str__(self):
        return repr(self.desc)

class Default (AbstractToken):
    '''
    A class whose instances always return L{desc} and do not advance the parser's cursor.
    '''
    def __call__(self, parser, origCursor):
        return self.desc
    def __str__(self):
        return repr(self.desc)

EmptyToken = Default('')

class CompositeToken (AbstractToken):
    '''
    A class whose instances match any of a number of tokens.
    
    @ivar desc: An iterable returning token objects.
    @type desc: iterable
    '''
    def __call__(self, parser, origCursor):
        for t in self.desc:
            r = parser.scan(t)
            if parser.last:
                return r
        raise NotMatched
    
    def __str__(self):
        if self in rstack:
            return '...'
        else:
            rstack.append(self)
            d = '(' + ' | '.join([repr(t) for t in self.desc]) + ')'
            rstack.pop()
            return d
    
    def __or__(self, other):
        if hasattr(other, '__iter__'):
            return CompositeToken(self.desc + list(other))
        else:
            return CompositeToken(self.desc + [other])
    
    def __ior__(self, other):
        if hasattr(other, '__iter__'):
            self.desc += list(other)
        else:
            self.desc.append(other)
        return self

class TokenSequence (AbstractToken):
    '''
    A class whose instances match a sequence of tokens. Returns a corresponding list of return values from L{ZestyParser.scan}.
    
    Some special types, L{Skip}, L{Omit}, and L{Only}, are allowed in the sequence. These are wrappers for other token objects adding special behaviours. If it encounters a L{Skip} token, it will process it with L{ZestyParser.skip}, ignore whether it matched, and not include it in the list. If it encounters a L{Omit} token, it will still require that it match (the default behaviour), but it will not be included in the list.
    
    If the sequence contains an L{Only} token, its result will be returned instead of the usual list, though it still requires that subsequent tokens match. Multiple L{Only} tokens are meaningless and L{TokenSequence}'s behavior in that case is undefined. 
    
    @ivar desc: An iterable returning token objects.
    @type desc: iterable
    '''
    def __call__(self, parser, origCursor):
        o = []
        only = False
        onlyVal = None
        for g in self.desc:
            r = parser.scan(g)
            if parser.last is None:
                raise NotMatched
            if isinstance(g, Only):
                only = True
                onlyVal = r
                continue
            if not isinstance(g, (Skip, Omit)) and not only:
                o.append(r)
        if only: #heh
            return onlyVal
        else:
            return o
        
    def __str__(self):
        if self in rstack:
            return '...'
        else:
            rstack.append(self)
            d = '(' + ' + '.join([repr(t) for t in self.desc]) + ')'
            rstack.pop()
            return d

    def __add__(self, other):
        if hasattr(other, '__iter__'):
            return TokenSequence(self.desc + list(other))
        else:
            return TokenSequence(self.desc + [other])
    
    def __iadd__(self, other):
        if hasattr(other, '__iter__'):
            self.desc += list(other)
        else:
            self.desc.append(other)
        return self

class TakeToken (AbstractToken):
    '''
    A class whose instances match and return a given number of characters from the parser's L{data<ZestyParser.data>}. Raises L{NotMatched} if not enough characters are left.
    '''
    
    def __init__(self, length, **kwargs):
        AbstractToken.__init__(self, length, **kwargs)
    
    def __call__(self, parser, start):
        end = start + self.desc
        if parser.len < end: raise NotMatched
        parser.cursor = end
        return parser.data[start:end]

class TokenSeries (AbstractToken):
    '''
    A particularly versatile class whose instances match one token multiple times (with a great degree of customizability).
    
    The properties L{skip}, L{prefix}, L{postfix}, and L{delimiter} are optional tokens which add structure to the series. It can be represented, approximately in the idioms of L{TokenSequence}, as follows::
    
        [Skip(skip) + Omit(prefix) + desc + Omit(postfix)] + [Skip(skip) + Omit(delimiter) + Skip(skip) + Omit(prefix) + desc + Omit(postfix)] + ... + Skip(skip)
    
    Or, if there is no delimiter::
    
        [Skip(skip) + Omit(prefix) + desc + Omit(postfix)] + ... + Skip(skip)
    
    @ivar desc: The token to match.
    @type desc: token
    @ivar min: The minimum number of times L{desc} must match.
    @type min: int
    @ivar max: The maximum number of times L{desc} will try to match.
    @type max: int
    @ivar skip: An optional token to skip between matches.
    @type skip: token
    @ivar prefix: An optional token to require (but omit from the return value) before each instance of L{token}.
    @type prefix: token
    @ivar postfix: An optional token to require (but omit from the return value) after each instance of L{token}.
    @type postfix: token
    @ivar delimiter: An optional token to require (but omit from the return value) between each instance of L{token}.
    @type delimiter: token
    @ivar until: An optional 2-tuple whose first item is a token, and whose second item is either a message or False. The presence of this property indicates that the token in C{until[0]} must match at the end of the series. If this fails, then if C{until[1]} is a message, a ParseError will be raised with that message; if it is False, NotMatched will be raised.
    '''
    def __init__(self, token, min=0, max=-1, skip=None, prefix=None, postfix=None, delimiter=None, until=None, includeDelimiter=False, **kwargs):
        AbstractToken.__init__(self, token, **kwargs)
        self.min, self.max, self.skip, self.prefix, self.postfix, self.delimiter, self.until, self.includeDelimiter = min, max, skip, prefix, postfix, delimiter, until, includeDelimiter

    def __call__(self, parser, origCursor):
        o = []
        i = 0
        done = False
        while i != self.max:
            c = parser.cursor
            if self.until and parser.skip(self.until[0]):
                done = True
                break
            if self.skip: parser.skip(self.skip)

            c = parser.cursor
            if i != 0 and self.delimiter is not None:
                d = parser.scan(self.delimiter)
                if parser.last is None: break
                if self.skip: parser.skip(self.skip)
            if self.prefix and not parser.skip(self.prefix): break
            t = parser.scan(self.desc)
            if parser.last is None: break
            if self.postfix and not parser.skip(self.postfix): break
            
            if i != 0 and self.includeDelimiter: o.append(d)
            o.append(t)
            i += 1
        if self.until and not done:
                parser.cursor = c
                if self.until[1]:
                    raise ParseError(parser, self.until[1])
                else:
                    raise NotMatched
        if i >= self.min:
            return o
        else:
            raise NotMatched
    
    def __str__(self):
        return repr(self.desc)

class Defer (AbstractToken):
    '''
    A token which takes a callable (generally a lambda) which takes no arguments and itself returns a token. A Defer instance, upon being called, will call this function, scan for the returned token, and return that return value. This is primarily intended to allow you to define tokens recursively; if you need to refer to a token that hasn't been defined yet, simply use C{Defer(lambda: T_SOME_TOKEN)}, where C{T_SOME_TOKEN} is the token's eventual name.
    '''
    
    def __init__(self, func, **kwargs):
        AbstractToken.__init__(self, func, **kwargs)
    
    def __call__(self, parser, origCursor):
        t = parser.scan(self.desc())
        if parser.last is None: raise NotMatched
        return t

class Skip (AbstractToken):
    '''
    See L{TokenSequence}.
    '''
    def __call__(self, parser, origCursor):
        parser.skip(self.desc)
    
    def pad(self, tok):
        '''
        Takes a TokenSequence and returns a copy with this L{Skip} token separating every element therein.
        
        @param tok: The token sequence to operate on.
        @type tok: L{TokenSequence}
        @return: L{TokenSequence}
        '''
        t = copy.copy(tok)
        o = []
        i = 0
        while i < len(t.desc):
            o.append(t.desc[i])
            if i != len(t.desc)-1:
                o.append(self)
            i += 1
        t.desc = o
        return t

class Omit (AbstractToken):
    '''
    See L{TokenSequence}.
    '''
    def __call__(self, parser, origCursor):
        if not parser.skip(self.desc):
            raise NotMatched

class Only (TokenWrapper):
    '''
    See L{TokenSequence}.
    '''

class Lookahead (AbstractToken):
    '''
    Scans for another token and returns its result as usual, but doesn't actually advance the parser's cursor.
    '''
    def __call__(self, parser, origCursor):
        t = parser.scan(self.desc)
        parser.cursor = origCursor
        if parser.last is None: raise NotMatched
        return t

class Negative (AbstractToken):
    '''
    Scans for another token, and only matches (returning True) if that token did not match.
    '''
    def __call__(self, parser, origCursor):
        parser.scan(self.desc)
        parser.cursor = origCursor
        if parser.last: raise NotMatched
        return True

class _EOF(AbstractToken):
    '''
    Matches returning None if the parser is at the end of its input.
    '''
    def __call__(self, parser, origCursor):
        if parser.cursor != parser.len: raise NotMatched
EOF = _EOF(None)

def Const(value):
    '''
    This is a factory function used for when you want an L{AbstractToken}-compatible callback that returns a constant. Example::
        RawToken('foo') >> Const('bar')
    
    This token matches 'foo' as usual, but always returns 'bar'.
    '''
    def f(r):
        return value
    return f