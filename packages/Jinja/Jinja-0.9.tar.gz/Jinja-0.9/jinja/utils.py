# -*- coding: utf-8 -*-
"""
    jinja utils
"""

from jinja.config import *
from jinja.exceptions import VariableDoesNotExist
from jinja.lib import stdlib

import string
import re


# Const for Regexes
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']

# Precompiles Regexes
integer_re = re.compile('^(\d+)$')
word_split_re = re.compile(r'(\s+)')
punctuation_re = re.compile(
    '^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join([re.escape(p) for p in LEADING_PUNCTUATION]),
    '|'.join([re.escape(p) for p in TRAILING_PUNCTUATION])))
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
template_tag_regex = re.compile(r'(%s.*?%s|%s.*?%s|%s.*?%s)(?sm)' % (
    re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END),
    re.escape(COMMENT_TAG_START), re.escape(COMMENT_TAG_END),
    re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END)))


try:
    "e".decode("string-escape")
    
    def string_unescape(s):
        return s.encode('utf-8').decode('string-escape').decode('utf-8')
except LookupError:
    # Python 2.2 has no "string-escape" codec
    def string_unescape(s):
        s = s.encode('utf-8')
        s = s.replace("'''", "'\\''")
        s = eval("'''" + s + "'''")
        s = s.decode('utf-8')
        return s

def resolve_variable(path, context):
    """resolves a variable in the following order:
        1.) None constants (None)
        2.) string constants ("some string")
        3.) integer constants (42)
        4.) boolean constants (True, False)
        5.) dictionary lookup (path['subpath']['subsubpath'])
        6.) list lookup: (path['subpath'][0])
        7.) attribute lookup (path.subpath.subsubpath)
    """
    assert path and isinstance(path, unicode)
    if path == u'None':
        return None
    elif path[0] in u'"\'' and path[0] == path[-1]:
        return string_unescape(path[1:-1])
    elif integer_re.match(path) is not None:
        return int(path)
    elif path.lower() in [u'true', u'false']:
        return path.lower() == u'true'
    else:
        current = context
        bits = path.split(u'.')
        for bit in bits:
            try:
                current = current[bit]
            # fail on key error
            # this ensures that the user can't access
            # attributes of dict like objects.
            except KeyError:
                raise VariableDoesNotExist()
            # on all other errors, try accessing indices and attributes
            except:
                try:
                    current = current[int(bit)]
                # IndexError: it _is_ a sequence, so fail if the index
                # is not found
                except IndexError:
                    raise VariableDoesNotExist()
                except:
                    try:
                        current = getattr(current, bit)
                    except AttributeError:
                        raise VariableDoesNotExist()
            if callable(current):
                try:
                    current = current()
                except:
                    raise VariableDoesNotExist()
    return current


def urlize(text, trim_url_limit=None, nofollow=False):
    """
    Converts any URLs in text into clickable links. Works on http://, https:// and
    www. links. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right thing.

    If trim_url_limit is not None, the URLs in link text will be limited to
    trim_url_limit characters.

    If nofollow is True, the URLs in link text will get a rel="nofollow" attribute.
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (x[:limit] + (len(x) >=limit and '...' or ''))  or x
    words = word_split_re.split(text)
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or ('@' not in middle and not middle.startswith('http://') and \
                    len(middle) > 0 and middle[0] in string.letters + string.digits and \
                    (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                middle = '<a href="http://%s"%s>%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = '<a href="%s"%s>%s</a>' % (middle, nofollow_attr, trim_url(middle))
            if '@' in middle and not middle.startswith('www.') and not ':' in middle \
                and simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return ''.join(words)


def registerfilter(name):
    """
    Small decorator for adding filters to the standardlib.
    Usage:
        @registerfilter('replace')
        def handle_replace(s, search, replace):
            return s.replace(search, replace)
    
    Requires python2.4 or higher.
    """
    def wrapped(f):
        stdlib.register_filter(name, f)
    return wrapped
