# -*- coding: utf-8 -*-
"""
=====
Jinja
=====

Jinja is a small but very fast und easy to use stand-alone template engine
written in pure python.

Since version 0.6 it uses a new parser that increases parsing performance
a lot by caching the nodelists on the harddisk if wanted.

It includes multiple template inheritance and other features like simple
value escaping...


Template Syntax
===============

This is a small example template in which you can see, how jinja's syntax
looks like:

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
    <head>
        <title>My Webpage</title>
    </head
    <body>
        <ul id="navigation">
        {% for item in navigation %}
            <li><a href="{{ item.href }}">{{ item.caption|escapexml }}</a></li>
        {% endfor %}
        </ul>

        <h1>My Webpage</h1>
        {{ variable }}
    </body>
    </html>

Usage
=====

Here a small example::

    from jinja import Template, Context, FileSystemLoader

    t = Template('mytemplate', FileSystemLoader('/path/to/the/templates'))
    c = Context({
        'navigation' [
            {'href': '#', 'caption': 'Index'},
            {'href': '#', 'caption': 'Spam'}
        ],
        'variable': 'hello world'
    })
    print t.render(c)

"""
from jinja.base import Context
from jinja.loader import FileSystemLoader, CachedFileSystemLoader, StringLoader,\
                         EggLoader, ChoiceLoader
import jinja.tags as tags
import jinja.filters as filters
import jinja.exceptions as exceptions
import jinja.lib as lib

__author__ = 'Armin Ronacher <armin.ronacher@active-4.com>'
__version__ = '0.8'
__license__ = 'BSD License'
__all__ = ['Context', 'Template', 'FileSystemLoader', 'CachedFileSystemLoader',
           'StringLoader', 'EggLoader', 'ChoiceLoader']


# XXX: accessing attributes on this loader will raise DeprecationWarnings
#      in future jinja versions (0.9) - (old loaders won't work in future
#      jinja version [1.0 or later])
class _OldLoader(object):

    def __init__(self, loader):
        self._loader = loader

    def load(self, name, parent=None):
        return self._loader.load(name)

    def load_and_compile(self, name, lib=None, parent=None):
        return self._loader.load_and_compile(name, lib)

    def load_and_compile_uncached(self, name, lib=None, parent=None):
        return self._loader.load_and_compile(name, lib)


class Template(object):

    def __init__(self, template_name, loader, lib=None):
        # support for jinja 0.7 loaders
        if not hasattr(loader, 'load_and_compile_uncached'):
            loader = _OldLoader(loader)
        self.nodelist = loader.load_and_compile(template_name, lib)

    def render(self, context):
        return self.nodelist.render(context)

