# -*- coding: utf-8 -*-
"""
    jinja builtin tokens
"""


__all__ = ['Token', 'NameVal', 'CommaVal', 'PipeVal', 'ValueToken',
           'StringVal', 'BoolVal', 'IntVal', 'NoneVal'] 


class Token(object):
    """Base Token class. All classes derive from this."""

    def __init__(self, token):
        self._token = token

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self._token)


class NameVal(Token):
    """A name token. A name token is [A-Za-z_][A-Za-z0-9_]* and only output in
    case its name doesn't match a different name."""

    def __call__(self):
        """Get the value of this token, interpreted."""
        return self._token


class CommaVal(Token):
    """Comma value to represent a literal comma (,) in the code."""

    def __init__(self):
        super(CommaVal, self).__init__(None)

    def __call__(self):
        """Get the value of this token, interpreted."""
        return None


class PipeVal(Token):
    """Pipe value to represent a literal pipe (|) in the code."""

    def __init__(self):
        super(PipeVal, self).__init__(None)

    def __call__(self):
        """Get the value of this token, interpreted."""
        return None


class ValueToken(Token):
    """Base class for all value tokens. A value token is a token which has a
    value."""


class StringVal(ValueToken):
    """String value token. A string value is defined as a string starting
    with \" or \' and escaped by the normal escaping rules of Python."""

    def __call__(self):
        """Get the value of this token, interpreted."""
        from jinja.utils import string_unescape
        return string_unescape(self._token[1:-1]).replace(
            u'\\{', u'{').replace(u'\\}', u'}')


class BoolVal(ValueToken):
    """Boolean value. A token that is either true or false."""

    def __call__(self):
        """Get the value of this token, interpreted."""
        return self._token.lower() == 'true'


class IntVal(ValueToken):
    """An integer value. It has a value and a base."""

    def __init__(self, token, base):
        super(IntVal, self).__init__(token)
        self._base = base

    def __call__(self):
        """Get the value of this token, interpreted."""
        return int(self._token, self._base)

    def __repr__(self):
        return '<%s: %r, base %r>' % (self.__class__.__name__,
                                      self._token, self._base)


class NoneVal(ValueToken):
    """The none value. A token that always has the value none."""

    def __call__(self):
        """Get the value of this token, interpreted."""
        return None
