# -*- coding: utf-8 -*-
"""
    jinja filters
    =============

    Contains all builtin template filters. Each template is able to use
    them by piping variables to them.

    The syntax is simple::

        {{ variable | filter }}

    This will passes variable to the filter "filter".
    In case of having more than one filter you can combine them::

        {{ variable | filter1 | filter2 }}

    If a filter requires an argument call it like this::

        {{ variable | filter1 argument1 argument2 | filter2 argument }}

    Each argument can be a Context variable or a constant value (string
    or integer).
"""
import re
from jinja.lib import stdlib


def stringfilter(oldfilter):
    """Decorator for filters that only operate on (unicode) strings.

    filter(s, *vars) --> filter(s, context, *vars)

    The decorated function will convert the first argument and all vars that
    are strings to unicode using the charset of the context.
    """
    def newfilter(s, context, *variables):
        if not isinstance(s, unicode):
            s = str(s).decode(context.charset, 'replace')
        for idx, var in enumerate(variables):
            if isinstance(var, str):
                variables[idx] = str(var).decode(context.charset, 'replace')
        return oldfilter(s, *variables)
    try:
        newfilter.__doc__ = oldfilter.__doc__
        newfilter.__name__ = oldfilter.__name__
    except TypeError:
        pass # __name__ assignment requires python 2.4
    return newfilter


def do_replace(s, old, new, count=None):
    """{{ s|replace old new[ count] }}

    Return a copy of s with all occurrences of substring
    old replaced by new. If the optional argument count is
    given, only the first count occurrences are replaced.
    """
    if count is None:
        return s.replace(old, new)
    return s.replace(old, new, count)
do_replace = stringfilter(do_replace)


def do_upper(s):
    """{{ s|upper }}

    Return a copy of s converted to uppercase.
    """
    return s.upper()
do_upper = stringfilter(do_upper)


def do_lower(s):
    """{{ s|lower }}

    Return a copy of s converted to lowercase.
    """
    return s.lower()
do_lower = stringfilter(do_lower)


def do_escapexml(s):
    """
    {{ s|escapexml }}

    XML escape &, <, and > in a string of data.
    """
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
do_escapexml = stringfilter(do_escapexml)


def do_e(s):
    """
    {{ s|e }}

    Alias for escapexml
    """
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
do_e = stringfilter(do_e)


def do_addslashes(s):
    """
    {{ s|addslashes }}

    Adds slashes to s.
    """
    return s.encode('utf-8').encode('string-escape').decode('utf-8')
do_addslashes = stringfilter(do_addslashes)


def do_capitalize(s):
    """
    {{ s|capitalize }}

    Return a copy of the string s with only its first character
    capitalized.
    """
    return s.capitalize()
do_capitalize = stringfilter(do_capitalize)


def do_title(s):
    """
    {{ s|title }}

    Return a titlecased version of s, i.e. words start with uppercase
    characters, all remaining cased characters have lowercase.
    """
    return s.title()
do_title = stringfilter(do_title)


def do_default(s, context, default_value=''):
    """
    {{ s|default[ default_value] }}

    In case of s isn't set or True default will return default_value
    which is '' per default.
    """
    if not s:
        return default_value
    return s


def do_join(sequence, context, d=''):
    """
    {{ sequence|join[ d] }}

    Return a string which is the concatenation of the strings in the
    sequence. The separator between elements is d which is an empty
    string per default.
    """
    try:
        if not isinstance(d, unicode):
            d = str(d).decode(context.charset, 'replace')
        return reduce(lambda x, y: str(x) + d + str(y), sequence)
    except:
        return str(sequence).decode(context.charset, 'replace')


def do_count(var, context):
    """
    {{ var|count }}

    Return the length of var. In case if getting an integer or float
    it will convert it into a string an return the length of the new
    string.
    If the object doesn't provide a __len__ function it will return
    zero.
    """
    try:
        if type(var) in (int, float, long):
            var = unicode(var)
        return unicode(len(var))
    except TypeError:
        return u'0'


def do_urlencode(s, plus=False):
    """
    {{ s|urlencode[ plus] }}

    Return the urlencoded value of s. For detailed informations have
    a look at the help page of "urllib.quote"

    If plus is set to 1 it will use the "urllib.quote_plus" method.
    """
    from urllib import quote, quote_plus
    if plus:
        return quote_plus(s)
    return quote(s)
do_urlencode = stringfilter(do_urlencode)


def do_striphtml(s):
    """
    {{ s|striphtml }}

    Return a plaintext version of s. (removes all html tags).
    """
    return re.sub(r'<[^>]*?>', '', s)
do_striphtml = stringfilter(do_striphtml)


def do_nl2pbr(s):
    """
    {{ s|nl2pbr }}

    Convert newlines into <p> and <br />s.
    """
    if not isinstance(s, basestring):
        s = str(s)
    s = re.sub(r'\r\n|\r|\n', '\n', s)
    paragraphs = re.split('\n{2,}', s)
    paragraphs = ['<p>%s</p>' % p.strip().replace('\n', '<br />')
                  for p in paragraphs]
    return '\n\n'.join(paragraphs)
do_nl2pbr = stringfilter(do_nl2pbr)


def do_nl2br(s):
    """
    {{ s|nl2br }}

    Convert newlines into <br />s.
    """
    return re.sub(r'\r\n|\r|\n', '<br />\n', s)
do_nl2br = stringfilter(do_nl2br)


def do_autolink(s, nofollow=False):
    """
    {{ s|autolink[ nofollow] }}

    Automatically creates <a> tags for recognized links.
    If nofollow is True autolink will add a rel=nofollow tag to the
    url.
    """
    from jinja.utils import urlize
    return urlize(s, nofollow=nofollow)
do_autolink = stringfilter(do_autolink)


def do_autolinktrunc(s, length=50, nofollow=False):
    """
    {{ s|autolink[ length[ nofollow]] }}

    Same as autolink but truncate the url to a given character limit.
    """
    from jinja.utils import urlize
    return urlize(s, length, nofollow)
do_autolinktrunc = stringfilter(do_autolinktrunc)


def do_reverse(iterable, context):
    """
    {{ iterable|reverse }}

    Return a reversed copy of a given iterable.
    """
    try:
        return list(reversed(iterable))
    except NameError:
        return list(iterable)[::-1]


def do_sort(iterable, context):
    """
    {{ iterable|sort }}

    Return a sorted copy of a given iterable.
    """
    try:
        return list(sorted(iterable))
    except NameError:
        l = []
        for item in iterable:
            l.append(item)
        l.sort()
        return l


def do_slice(iterable, context, *args):
    """
    {{ iterable|slice start, end, step }}

    Return a slice of an iterable.
    """
    if not hasattr(iterable, '__getslice__') or\
       not hasattr(iterable, '__getitem__'):
        try:
            iterable = list(iterable)
        except:
            iterable = str(iterable).decode(context.charset, 'replace')
    try:
        return iterable[slice(*[int(arg) for arg in args[:3]])]
    except:
        return iterable


def do_deletedouble(iterable, context):
    """
    {{ iterable|deletedouble }}

    Remove double items in an iterable.
    """
    try:
        return list(set(iterable))
    except NameError:
        from sets import Set
        return list(Set(iterable))


def do_format(s, context, f):
    """
    {{ s|format f }}

    Apply python string format f on s. The leading "%" is left out.
    """
    return ('%' + f) % s


def do_indent(s, width=4, indentfirst=False, usetab=False):
    """
    {{ s|indent[ width[ indentfirst[ usetab]]] }}

    Return a copy of s, each line indented by width spaces.
    If usetab is True it the filter will use tabs for indenting.
    If indentfirst is given it will also indent the first line.
    """
    indention = ((usetab) and u'\t' or u' ') * width
    if indentfirst:
        return u'\n'.join([indention + line for line in s.splitlines()])
    else:
        return s.replace(u'\n', u'\n' + indention)
do_indent = stringfilter(do_indent)


def do_truncate(s, length=255, killwords=False, end='...'):
    """
    {{ s|truncate[ length[ killwords[ end]]] }}

    Return a truncated copy of s. If killwords is True the filter
    will cut the text at length and append end. Otherwise it will
    try to save the last word and append end.
    """
    if len(s) <= length:
        return s
    if killwords:
        return s[:length] + end
    words = s.split(' ')
    result = []
    m = 0
    for word in words:
        m += len(word) + 1
        if m > length:
            break
        result.append(word)
    return ' '.join(result)
do_truncate = stringfilter(do_truncate)


def do_wordwrap(s, pos=79, hard=False):
    """
    {{ s|wordwrap[ hard] }}

    Return a copy of s, word get wrapped at pos, if hard is True
    word might get split.
    """
    if len(s) < pos:
        return s
    if hard:
        return '\n'.join([s[idx:idx + pos] for idx in xrange(0, len(s), pos)])
    # code from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
    return reduce(lambda line, word, pos=pos: '%s%s%s' %
                  (line, ' \n'[(len(line)-line.rfind('\n')-1 +
                                len(word.split('\n',1)[0]) >= pos)],
                   word), s.split(' '))
do_wordwrap = stringfilter(do_wordwrap)


def do_textile(s):
    """
    {{ s|textile }}

    Return a textfile parsed copy of s.

        requires the PyTextile library available at
        http://dealmeida.net/projects/textile/
    """
    from textile import textile
    return textile(s)
do_textile = stringfilter(do_textile)


def do_markdown(s):
    """
    {{ s|markdown }}

    Return a markdown parsed copy of s.

        requires the Python-markdown library from
        http://www.freewisdom.org/projects/python-markdown/
    """
    from markdown import markdown
    return markdown(s)
do_markdown = stringfilter(do_markdown)


def do_rst(s):
    """
    {{ s|rst }}

    Return a reStructuredText parsed copy of s.

        requires docutils from http://docutils.sourceforge.net/
    """
    try:
        from docutils.core import publish_parts
        parts = publish_parts(source=s, writer_name='html4css1')
        return parts['fragment']
    except:
        return s
do_rst = stringfilter(do_rst)


def do_cut(s, context, char):
    """
    {{ s|cut char }}

    Equivalent to {{ s|replace char '' }}.
    """
    if not isinstance(char, unicode):
        char = str(char).decode(context.charset, 'replace')
    return do_replace(s, context, char, u'')


def do_cleanup(s):
    """
    {{ s|cleanup }}

    Remove double whitespaces.
    """
    return ' '.join(s.split())
do_cleanup = stringfilter(do_cleanup)


def do_filesizeformat(i, context):
    """
    {{ i|filesizeformat }}

    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    bytes = float(i)
    if bytes < 1024:
        return u"%d Byte%s" % (bytes, bytes != 1 and u's' or u'')
    if bytes < 1024 * 1024:
        return u"%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return u"%.1f MB" % (bytes / (1024 * 1024))
    return u"%.1f GB" % (bytes / (1024 * 1024 * 1024))


def do_wordcount(s):
    """
    {{ s|wordcount }}

    Return the number of words.
    """
    return len(s.split())
do_wordcount = stringfilter(do_wordcount)


def do_strip(s, chars='\r\n\t '):
    """
    {{ s|strip[ chars] }}

    Return a copy of s with leading and trailing whitespace removed.
    If chars is given and not None, remove characters in chars instead.
    """
    return s.strip(chars)
do_strip = stringfilter(do_strip)


def do_regexreplace(s, search, replace):
    """
    {{ s|regexreplace search replace }}

    Perform a re.sub on s

    Example:
        {{ s|regexreplace '\\[b\\](.*?)\\[/b\\](?i)' '<strong>\\1</strong>' }}
    """
    return re.sub(search, replace, s)
do_regexreplace = stringfilter(do_regexreplace)


def do_decode(s, context, encoding):
    """
    {{ s|decode encoding }}
    
    Decode s to unicode with given encoding instead of the context's default.
    
    Example:
        {{ s|decode 'latin-1' }}
    """
    if isinstance(s, unicode):
        # this is already unicode, so do nothing
        return s
    return str(s).decode(encoding, 'replace')


def do_str(obj, context):
    """
    {{ obj|str }}

    Converts an object to a string
    """
    if isinstance(obj, unicode):
        # this is already unicode, so do nothing
        return obj
    return str(obj).decode(context.charset, 'replace')


def do_int(obj, context, default=0):
    """
    {{ obj|int }}

    Converts an object to an integer if possible,
    otherwise returns default
    """
    try:
        return int(obj)
    except:
        try:
            return int(default)
        except:
            return 0


def do_float(obj, context, default=0.0):
    """
    {{ obj|float }}

    Converts an object to a float if possible,
    otherwise returns default
    """
    try:
        return float(obj)
    except:
        try:
            return float(default)
        except:
            return 0.0


def do_bool(obj, context, default=False):
    """
    {{ obj|bool }}

    Converts an object to a bool if possible,
    otherwise returns default
    """
    try:
        return bool(obj)
    except:
        try:
            return bool(default)
        except:
            return False


def do_makebool(obj, context, default=False):
    """
    {{ obj|makebool }}

    Guesses an boolean (true, on, 1, yes)
    """
    def check(obj):
        if not isinstance(obj, basestring):
            obj = str(obj).lower()
        else:
            obj = obj.lower()
        if obj in ('true', '1', 'yes', 'on'):
            return True
        elif obj in ('false', '0', 'no', 'off'):
            return False
    val = check(obj)
    if val is None:
        val = check(default)
        if val is None:
            return False
    return val


builtin_filters = {
    'replace':          do_replace,
    'upper':            do_upper,
    'lower':            do_lower,
    'escapexml':        do_escapexml,
    'e':                do_e,
    'addslashes':       do_addslashes,
    'capitalize':       do_capitalize,
    'title':            do_title,
    'default':          do_default,
    'join':             do_join,
    'count':            do_count,
    'urlencode':        do_urlencode,
    'striphtml':        do_striphtml,
    'nl2pbr':           do_nl2pbr,
    'nl2br':            do_nl2br,
    'autolink':         do_autolink,
    'autolinktrunc':    do_autolinktrunc,
    'reverse':          do_reverse,
    'sort':             do_sort,
    'slice':            do_slice,
    'deletedouble':     do_deletedouble,
    'format':           do_format,
    'indent':           do_indent,
    'truncate':         do_truncate,
    'wordwrap':         do_wordwrap,
    'textile':          do_textile,
    'markdown':         do_markdown,
    'rst':              do_rst,
    'cut':              do_cut,
    'cleanup':          do_cleanup,
    'filesizeformat':   do_filesizeformat,
    'wordcount':        do_wordcount,
    'strip':            do_strip,
    'regexreplace':     do_regexreplace,
    'decode':           do_decode,
    'str':              do_str,
    'int':              do_int,
    'float':            do_float,
    'bool':             do_bool,
    'makebool':         do_makebool,
}

for name, handler in builtin_filters.iteritems():
    stdlib.register_filter(name, handler)
