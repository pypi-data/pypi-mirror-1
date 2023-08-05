# -*- coding: utf-8 -*-
"""
    Jinja Template
    --------------
    Base Module
"""
from __future__ import generators

from jinja.config import *
from jinja.exceptions import TemplateSyntaxError
from jinja.nodes import Node, TextNode
from jinja.utils import template_tag_regex
from jinja.lib import stdlib


# Tokenizer
TOKEN_TEXT = 0
TOKEN_VAR = 1
TOKEN_BLOCK = 2


class Context(object):
    
    def __init__(self, d=None, charset='utf-8'):
        self.dicts = [d or {}]
        self.charset = charset
        self.registry = {}
        self.filters = None

    def __repr__(self):
        return repr(self.dicts)

    def __iter__(self):
        for d in self.dicts:
            yield d

    def iterdata(self):
        for d in self.dicts:
            for key, value in d.iteritems():
                yield key, value

    def dictrepr(self):
        return dict(list(self.iterdata()))

    def push(self):
        self.dicts = [{}] + self.dicts

    def pop(self):
        if len(self.dicts) == 1:
            self.dicts = [{}]
        del self.dicts[0]

    def __setitem__(self, key, value):
        """Set a variable in the current context."""
        self.dicts[0][key] = value

    def __getitem__(self, key):
        """
        Get a variable's value, starting at the current context
        and going upward.

        First it also checks for the special variable called
        CONTEXT returning the full context.
        """
        if key == 'CONTEXT':
            return self
        for d in self.dicts:
            if key in d:
                return d[key]
        return ''

    def __delitem__(self, key):
        """Delete a variable from the context."""
        for d in self.dicts:
            if key in d:
                del d[key]
                return

    def __contains__(self, key):
        return self.has_key(key)

    def has_key(self, key):
        for d in self.dicts:
            if key in d:
                return True
        return False

    def get(self, key, otherwise=None):
        for d in self.dicts:
            if key in d:
                return d[key]
        return otherwise

    def update(self, other_dict):
        """
        Like dict.update(). Pushes an entire dictionary's keys
        and values onto the context.
        """
        self.dicts = [other_dict] + self.dicts


class Token(object):

    def __init__(self, token_type, contents):
        self.token_type = token_type
        self.contents = contents

    def __str__(self):
        return '<%sToken "%s">' % ({
            TOKEN_TEXT:     'Text',
            TOKEN_VAR:      'Var',
            TOKEN_BLOCK:    'Block'
        }[self.token_type], self.contents[:].replace('\n', ''))
    __repr__ = __str__


class NodeList(list):

    def render(self, context):
        bits = []
        for node in self:
            if isinstance(node, Node):
                bits.append(node.render(context))
            else:
                bits.append(node)
        return u''.join(bits)
    
    def findnodes(self):
        try:
            nodes = set()
        except NameError:
            from sets import Set
            nodes = Set()
        for node in self:
            nodes.update(node.findnodes())
        return nodes
        
    def get_nodes_by_type(self, nodetype):
        for node in self.findnodes():
            if isinstance(node, nodetype):
                yield node


class Lexer(object):

    def __init__(self, template):
        self.template = template
        
    def tokenize(self):
        return [self.create_token(tag) for tag in
                template_tag_regex.split(self.template) if self.check_tag(tag)]
        
    def check_tag(self, tag):
        return not tag.startswith(COMMENT_TAG_START)
        
    def create_token(self, tag):
        if tag.startswith(VARIABLE_TAG_START):
            token = Token(TOKEN_VAR, tag[len(VARIABLE_TAG_START):
                                         -len(VARIABLE_TAG_END)].strip())
        elif tag.startswith(BLOCK_TAG_START):
            token = Token(TOKEN_BLOCK, tag[len(BLOCK_TAG_START):
                                           -len(BLOCK_TAG_END)].strip())
        else:
            token = Token(TOKEN_TEXT, tag)
        return token


class Parser(object):

    def __init__(self, tokens, loader, lib=None, template_name=None):
        self.first = True
        self.tokens = tokens
        self.library = lib or stdlib
        self.loader = loader
        self.template_name = template_name

    def parse(self, parse_until=None):
        if parse_until is None:
            parse_until = []
        nodelist = NodeList()
        while self.tokens:
            token = self.pop_token()
            # plain text token result in a text node
            if token.token_type == TOKEN_TEXT:
                if token.contents:
                    nodelist.append(TextNode(self, token.contents))
            # we found a var token, it's only a shortcut for {% print ... %}
            elif token.token_type == TOKEN_VAR:
                if token.contents:
                    nodelist.append(self.library.parse(self, 'print %s' %
                                                       token.contents))
                else:
                    raise TemplateSyntaxError, 'variable is empty'
            # ney. looks like a block, give it to the library parser
            elif token.token_type == TOKEN_BLOCK:
                if token.contents in parse_until:
                    self.tokens.insert(0, token)
                    return nodelist
                nodelist.append(self.library.parse(self, token.contents))
            if nodelist:
                self.first = False
        if parse_until:
            raise TemplateSyntaxError, 'closing tag %s is missing' % parse_until
        return nodelist

    def pop_token(self):
        return self.tokens.pop(0)

    def get_last_token(self):
        return self.tokens.pop(0)
        
    def remove_dangling_token(self):
        del self.tokens[0]

    def subparse(self, endtag):
        result = self.parse([endtag])
        self.remove_dangling_token()
        return result
    
    def forkparse(self, shift, endtag):
        result_one = self.parse([shift, endtag])
        token = self.get_last_token()
        if token.contents == shift:
            result_two = self.parse([endtag])
            self.remove_dangling_token()
        else:
            result_two = NodeList()
        return result_one, result_two
