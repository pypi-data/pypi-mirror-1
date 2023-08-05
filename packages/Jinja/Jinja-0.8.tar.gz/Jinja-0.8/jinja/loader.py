# -*- coding: utf-8 -*-
"""
    jinja template loader
"""

from jinja.base import Lexer, Parser
from jinja.exceptions import TemplateDoesNotExist, TemplateSyntaxError, \
                             TemplateCharsetError

import os
from md5 import md5
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    from pkg_resources import resource_exists, resource_string
except ImportError:
    resource_exists = resource_string = None


__all__ = ['FileSystemLoader', 'CachedFileSystemLoader', 'StringLoader',
           'EggLoader', 'ChoiceLoader']


class BaseLoader(object):

    def load(self, name, parent=None):
        """This method isn't allowed to cache the data"""
        raise NotImplementedError()

    def load_and_compile(self, name, lib=None, parent=None):
        """Get's called when the template requires an nodelist
        to render on."""
        template = self.load(name, parent)
        lexer = Lexer(template)
        parser = Parser(lexer.tokenize(), self, lib)
        return parser.parse()

    def load_and_compile_uncached(self, name, lib=None, parent=None):
        """Get's called for the extends tag to get a fresh
        nodelist to manipulate."""
        return self.load_and_compile(name, lib, parent)


class FileSystemLoader(BaseLoader):
    """
    Loads templates from the filesystem::

        from jinja import FileSystemLoader

        loader = FileSystemLoader('/template/search/path')
    """

    def __init__(self, path, suffix='.html', charset='utf-8'):
        self.path = path
        self.suffix = suffix
        self.charset = charset
        
    def load(self, name, parent=None):
        name = os.sep.join([p for p in name.split(os.sep) if p and p[0] != '.'])
        fn = os.path.join(self.path, name) + self.suffix
        if os.path.exists(fn):
            contents = file(fn).read()
        else:
            raise TemplateDoesNotExist(name)
        try:
            return contents.decode(self.charset)
        except UnicodeDecodeError, e:
            raise TemplateCharsetError("Could not decode template '%s'" % fn, e)


class CachedFileSystemLoader(FileSystemLoader):
    """
    Same as ``FileSystemLoader`` but caches the parsed nodelist in a binary
    cPickle dump.
    """

    def __init__(self, path, suffix='.html', cache_dir=None, charset='utf-8'):
        super(CachedFileSystemLoader, self).__init__(path, suffix, charset)
        if cache_dir is None:
            self.cache_dir = path
            self.prefix = True
        else:
            self.cache_dir = cache_dir
            self.prefix = False

    def load_and_compile(self, name, lib=None, parent=None):
        if self.prefix:
            prefix = '.'
        else:
            prefix = ''
        hash_ = md5('%s/%s' % (self.path, name)).hexdigest()
        cache_name = os.path.join(self.cache_dir, prefix + hash_) + '.cache'
        template_name = os.path.join(self.path, name) + self.suffix
        
        if not os.path.exists(cache_name) or \
           os.path.getmtime(cache_name) < os.path.getmtime(template_name):
            nodelist = FileSystemLoader.load_and_compile(self, name, lib, parent)
            try:
                pickle.dump(nodelist, file(cache_name, 'wb'), protocol=2)
            except IOError:
                pass
        else:
            try:
                nodelist = pickle.load(file(cache_name, 'rb'))
            except IOError:
                nodelist = FileSystemLoader.load_and_compile(self, name, lib.
                                                             parent)
        return nodelist

    def load_and_compile_uncached(self, name, lib=None, parent=None):
        super(CachedFileSystemLoader, self).load_and_compile(name, lib, parent)


class StringLoader(BaseLoader):
    """
    A non thread safe version of a loader getting their templates
    from strings. If you want a thread safe behaviour you have to
    create a new loader for each template::

        from jinja import Template, StringLoader
        t = Template('''my template here''', StringLoader())
    """

    def __init__(self, charset='utf-8'):
        self.charset = charset
        self.template = False
    
    def load(self, tpl, parent=None):
        try:
            return unicode(tpl, self.charset)
        except UnicodeDecodeError, e:
            raise TemplateCharsetError('Could not decode template', e)

    def load_and_compile(self, name, lib=None, parent=None):
        if self.template:
            raise TemplateSyntaxError('StringLoader doesn\'t allow '
                                      'template inheritance')
        self.template = True
        rv = super(StringLoader, self).load_and_compile(name, lib, parent)
        self.template = False
        return rv


class EggLoader(FileSystemLoader):
    """
    Loads templates from an egg::

        from jinja import EggLoader

        loader = EggLoader('MyEgg', 'internal/path/to/templates')
    """
    # contributed by Jon Rosebaugh
    
    def __init__(self, package, path, suffix='.html', charset='utf-8'):
        if resource_exists is resource_string is None:
            raise RuntimeError('pkg_resources not found')
        super(EggLoader, self).__init__(path, suffix, charset)
        self.package = package

    def load(self, name, parent=None):
        name = '/'.join([p for p in name.split('/') if p and p[0] != '.'])
        name = '/'.join([self.path, name]) + self.suffix
        if resource_exists(self.package, name):
            contents = resource_string(self.package, name)
        else:
            raise TemplateDoesNotExist(name)
        try:
            return contents.decode(self.charset)
        except UnicodeDecodeError, e:
            raise TemplateCharsetError("Could not decode template '%s'" % fn, e)


class ChoiceLoader(object):
    """
    Takes a number of loader instances.

    The ``load`` and ``load_and_compile`` method try to to call the
    functions of all given loaders::

        from jinja import ChoiceLoader, FileSystemLoader, EggLoader

        loader = ChoiceLoader(
            FileSystemLoader('/path/to/my/templates'),
            EggLoader('MyEgg', 'internal/path/to/templates')
        )
    """

    def __init__(self, *loaders):
        self.loaders = loaders

    def load(self, name, parent=None):
        for loader in self.loaders:
            try:
                return loader.load(name, parent=None)
            except TemplateDoesNotExist:
                continue
        raise TemplateDoesNotExist(name)

    def load_and_compile(self, name, lib=None, parent=None):
        for loader in self.loaders:
            try:
                return loader.load_and_compile(name, lib, parent)
            except TemplateDoesNotExist:
                continue
        raise TemplateDoesNotExist(name)

    def load_and_compile_uncached(self, name, lib=None, parent=None):
        for loader in self.loaders:
            try:
                return loader.load_and_compile_uncached(name, lib, parent)
            except TemplateDoesNotExist:
                continue
        raise TemplateDoesNotExist(name)
