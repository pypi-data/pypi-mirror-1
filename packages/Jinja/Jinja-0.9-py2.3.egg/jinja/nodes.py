# -*- coding: utf-8 -*-
"""
    jinja builtin nodes
"""
from __future__ import generators

from jinja.exceptions import VariableDoesNotExist, TemplateSyntaxError, \
                             TemplateCharsetError
from jinja.tokens import NameVal, ValueToken, CommaVal
from jinja.utils import resolve_variable

__all__ = ['Node', 'TextNode', 'KeywordNode', 'VariableNode', 'ValueNode',
           'ChoiceNode', 'CollectionNode']


class Node(object):
    """class for basenode."""
    
    def findnodes(self):
        yield self


class TextNode(Node):
    
    def __init__(self, parser, data):
        self._data = data
        
    def render(self, context):
        return self._data
        
    def __str__(self):
        return self._data
        
    def __repr__(self):
        return '<TextNode: %r>' % self._data[:20]

class KeywordNode(Node):

    def __init__(self, name):
        self._name = name

    def match(self, node):
        if not isinstance(node, NameVal):
            return 0, None, None
        if self._name != node().lower():
            return 0, None, None
        return 10, self, None
        
    def __cmp__(self, other):
        if isinstance(other, basestring):
            return cmp(self._name.lower(), other.lower())
        elif isinstance(other, KeywordNode):
            return cmp(self._name.lower(), other._name.lower())
        else:
            raise TypeError, 'can\'t compare %r and %r types' % (
                self.__class__.__name__, other.__class__.__name__
            )

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self._name)


class VariableNode(Node):

    def __init__(self, name=None):
        self._name = name
        self._filters = None

    def match(self, node):
        if not isinstance(node, NameVal) or \
           (self._name is not None and self._name != node()):
            return 0, None, None
        if self._name:
            return 10, self.__class__(node()), None
        else:
            return 0, self.__class__(node()), None

    def resolve(self, context, silent=True, default=u''):
        try:
            return resolve_variable(self._name, context)
        except VariableDoesNotExist:
            if silent:
                return default
            raise
            
    def define(self, context, value):
        context[self._name] = value
        
    def unset(self, context):
        if self._name in context:
            del context[self._name]
        
    def render(self, context):
        result = self.resolve(context)
        if not isinstance(result, unicode):
            try:
                return str(result).decode(context.charset)
            except UnicodeError, e:
                raise TemplateCharsetError("Could not resolve variable '%s'" %
                                           self._name, e)
        return result

    def __repr__(self):
        if self._name is not None:
            return '<%s: %r>' % (self.__class__.__name__, self._name)
        else:
            return '<%s>' % self.__class__.__name__


class ValueNode(Node):

    def __init__(self, value=()):
        self._value = value

    def match(self, node):
        if not isinstance(node, ValueToken):
            return 0, None, None
        return 10, self.__class__(node()), None

    def resolve(self, context=None, silent=True):
        return self._value

    def render(self, context):
        if not isinstance(self._value, unicode):
            try:
                return str(self._value).decode(context.charset)
            except UnicodeError, e:
                raise TemplateCharsetError("Could not resolve value %r" %
                                           self._value, e)
        return self._value

    def __repr__(self):
        if self._value != ():
            return "<%s: %r>" % (self.__class__.__name__, self._value)
        else:
            return "<%s>" % self.__class__.__name__


class ChoiceNode(Node):

    def __init__(self, *values):
        self._values = values or [ValueNode(), VariableNode()]

    def match(self, node):
        rv = []
        for value in self._values:
            score, match, next = value.match(node)
            if match is not None:
                rv.append((score, match, next))
        rv.sort()
        if not rv:
            return 0, None, None
        return rv[-1]


class CollectionNode(Node):

    def __init__(self, *values):
        self._values = values or [ValueNode(), VariableNode()]

    def match(self, node):
        if node is None:
            return 0, [], None
        for value in self._values:
            score, match, next = value.match(node)
            if match is not None:
                return score, [match], _CollectionNodeComma(self)
        return 0, None, None
        
    def findnodes(self):
        for node in self._values:
            if not isinstance(node, Node):
                continue
            for n in node.findnodes():
                yield n


class _CollectionNodeComma(Node):

    def __init__(self, valuelist):
        self._valuelist = valuelist

    def match(self, node):
        if not isinstance(node, CommaVal):
            return 0, None, None
        return 10, None, self._valuelist
