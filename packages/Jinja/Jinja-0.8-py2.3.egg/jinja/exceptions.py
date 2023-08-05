# -*- coding: utf-8 -*-
"""
    jinja exceptions
"""

class SilentVariableFailure(Exception):
    pass


class VariableDoesNotExist(Exception):
    pass


class TemplateCharsetError(Exception):
    def __init__(self, msg, exc):
        self._msg = msg
        self._exc = exc

    def __str__(self):
        return '%s:\n%s' % (self._msg, self._exc)

    def __repr__(self):
        return '%s:\n%r' % (self._msg, self._exc)


class TemplateSyntaxError(Exception):
    pass


class TemplateRuntimeError(Exception):
    pass


class TemplateDoesNotExist(Exception):
    pass


class ContextPopException(Exception):
    pass


class TagLexerError(ValueError):

    def __init__(self, msg, pos, databuf):
        from jinja.tagparser import ERROR_KEEP
        self._msg = msg
        self._data = ''.join(databuf)[max(0, pos - ERROR_KEEP): pos + ERROR_KEEP]
        self._datapos = min(pos, max(0, pos - ERROR_KEEP) + ERROR_KEEP)
        self._pos = pos + 1

    def __str__(self):
        return '%s at %s.' % (self._msg, self._pos)

    def __repr__(self):
        return '<%s: %s at %s>' % (self.__class__.__name__, self._msg, self._pos)

