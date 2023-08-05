# -*- coding: utf-8 -*-
"""
    jinja tag library
"""

from jinja.tagparser import Parser, CHAIN_PROVIDER, CHAIN_FILTER


class ParserLibrary(object):

    def __init__(self, base=None):
        if base is None:
            self.rules = {}
        else:
            self.rules = base.rules.copy()

    def __repr__(self):
        return '<ParserLibrary (%d filters, %d tags)>' % (
            len(self.filters), len(self.tags))

    def clone(self):
        """Clone the current library."""
        return ParserLibrary(self)
    
    def register_tag(self, tag):
        """Register a new Tag."""
        for name, rule in tag.rules.iteritems():
            self.rules[(tag, name)] = (CHAIN_PROVIDER, rule)
    
    def register_filter(self, name, f):
        """Register a filter node."""
        from jinja.nodes import KeywordNode, CollectionNode
        rule = [KeywordNode(name), CollectionNode()]
        if (f, None) in self.rules:
            raise TypeError('filter already registered')
        else:
            self.rules[f, None] = (CHAIN_FILTER, rule)

    def unregister_tag(self, tag):
        """Unregister a tag."""
        for name, rule in tag.rules.iteritems():
            key = tag, name
            if key in self.rules:
                del self.rules[key]

    def parse(self, tmplparser, line):
        parser = Parser(self.rules)
        parser.feed(line)
        parser.finish()

        stack = []
        tag = None
        tag_args = None
        for (handler, name), args in parser.collect():
            if tag is None:
                tag = handler
                tag_args = (name, args)
            else:
                stack.append((handler, name, args))
        if not tag is None:
            return tag(tmplparser, tag_args[0], tag_args[1], stack)

    def register(self, name):
        """
        Decorator for registering filters:

        @stdlib.register("name")
        def myfilter(...): pass
        """
        def wrapped(f):
            self.register_filter(name, f)
            return f
        return wrapped

    def filters(self):
        """Return the list of filters."""
        result = {}
        for (tag, name), (chain_type, rule) in self.rules.iteritems():
            if name is None:
                result[rule[0]._name] = tag
        return result
    filters = property(filters, doc=filters.__doc__)

    def tags(self):
        """Return the list of registered tags."""
        result = set()
        for (tag, name), (chain_type, rule) in self.rules.iteritems():
            if not name is None:
                result.add(tag)
        return list(result)
    tags = property(tags, doc=tags.__doc__)


stdlib = ParserLibrary()
