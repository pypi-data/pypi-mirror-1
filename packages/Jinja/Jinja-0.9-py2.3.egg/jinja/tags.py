# -*- coding: utf-8 -*-
"""
    jinja builtin tags
"""
from __future__ import generators
from jinja.exceptions import TemplateRuntimeError, TemplateSyntaxError, \
                             TemplateCharsetError
from jinja.lib import stdlib
from jinja.nodes import *


class VariableTag(Node):
    """
    Variable Tag
    ============
    
    Prints a variable stored in the context. With a dot "." you can access
    attributes and items::
    
        ======================== ============================
        Usage                    Result
        ======================== ============================
        ``user.username``        ``user['username']``
        ``arg.0``                ``arg[0]``
        ``object.attribute``     ``object.attribute``
        ======================== ============================
    
    Usage::
    
        {% print variable %}
        {% print variable | somefilter "filterarg" %}
   
    Instead of print you can use the following shortcuts::
        
        {{ variable }}
        {{ variable | somefilter | otherfilter "filterarg" }}
    """
    
    rules = {
        'default': [KeywordNode('print'), ChoiceNode()]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        self._variable = handler_args[1]
        self._filters = [(f, args[1:][0]) for f, _, args in stack]
        
    def findnodes(self):
        yield self._variable
        
    def render(self, context):
        if context.filters is None:
            filters = self._filters[:]
        else:
            filters = self._filters + context.filters
        # there aren't any filters applied to this variable, so render it
        if not filters:
            return self._variable.render(context)
        # we have some of these cute things, apply them filter by filter
        var = self._variable.resolve(context)
        for f, args in filters:
            var = f(var, context, *[arg.resolve(context) for arg in args])
        if not isinstance(var, unicode):
            try:
                return str(var).decode(context.charset)
            except UnicodeError, e:
                raise TemplateCharsetError('Could not convert variable', e)
        return var
        
    def __repr__(self):
        return '<VariableTag: %r|%r>' % (self._variable, self._filters)

stdlib.register_tag(VariableTag)


class ForLoopTag(Node):
    """
    For Loop
    ========
    
    Iterate through the given list. This can eighter be a hardcoded
    list ("row1", "row2", "row3"...) or a variable containing an iterable.
    
    The syntax is "for ITEM in ITERABLE[ reversed]" where reversed is
    optional. You can access the current iteration from the loop body
    with {{ ITEM }}.
        
    The for loop sets a number of variables available within the loop:

        ======================= =======================================
        Variable                Description
        ======================= =======================================
        ``loop.counter``        The current iteration of the loop
        ``loop.counter0``       The current iteration of the loop,
                                starting counting by 0.
        ``loop.revcounter``     The number of iterations from the end
                                of the loop.
        ``loop.revcounter0``    The number of iterations from the end
                                of the loop, starting counting by 0.
        ``loop.length0``        Lenght of the loop, zero indexed
        ``loop.length``         Length of the loop.
        ``loop.first``          True if first iteration.
        ``loop.last``           True if last iteration.
        ``loop.even``           True if current iteration is even.
        ``loop.odd``            True if current iteration is odd.
        ``loop.parent           The context of the parent loop.
        ======================= =======================================


    Example Usage::
    
        {% for user in userlist %}
            {{ user.name }} on index {{ loop.counter0 }}     
        {% endfor %}
        
    And here a hardcoded version::
        
        {% for row in "row1", "row2", "row3" reversed %}
            {{ row }}
        {% endfor %}
        
    Loops can also have a ``elsefor`` statement::
        
        {% for user in users %}
            {{ user }}
        {% elsefor %}
            no users found
        {% endfor %}
    
    This acts the same as::
        
        {% if users %}
            {% for user in users %}
                {{ user }}
            {% endfor %}
        {% else %}
            no users found
        {% endif %}
    """
    
    rules = {
        'normal': [
            KeywordNode('for'), VariableNode(), KeywordNode('in'),
            CollectionNode()],
        'reversed': [
            KeywordNode('for'), VariableNode(), KeywordNode('in'),
            CollectionNode(), KeywordNode('reversed')]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        self._reversed = matched_tag == 'reversed'
        self._variable = handler_args[1]
        self._iterable = handler_args[3]
        self._body_loop, self._body_else = parser.forkparse('elsefor', 'endfor')
        
    def findnodes(self):
        yield self
        for node in self._body_loop:
            for n in node.findnodes():
                yield n
        for node in self._body_else:
            for n in node.findnodes():
                yield n
        
    def render(self, context, iterable=None):
        from jinja.base import NodeList
        nodelist = NodeList()
        if iterable is None:
            if len(self._iterable) == 1 and isinstance(self._iterable[0],
                                                       VariableNode):
                iterable = self._iterable[0].resolve(context, default=[])
            elif len(self._iterable) > 1:
                iterable = [v.resolve(context) for v in self._iterable]
            else:
                raise TemplateRuntimeError('for loop requires a list')
        
        # get len of iterable
        # if not available iterate through all elements and count
        # the iterations
        try:
            len_values = len(iterable)
        except TypeError:
            iterable = list(iterable)
            len_values = len(iterable)

        # find parent loop
        if 'loop' in context:
            parent = context['loop']
        else:
            parent = {}
        
        # create a new layer for new context variables
        context.push()
        
        # reverse iterator if required
        # this should also work for iterators that are not sequence or
        # on python versions older than 2.4
        if self._reversed:
            try:
                iterable = reversed(iterable)
            except (NameError, TypeError):
                if hasattr(iterable, '__len__'):
                    def save_reversed(i):
                        idx = 0
                        while idx < len(i):
                            yield i[idx]
                            idx += 1
                    iterable = save_reversed(iterable)
                else:
                    iterable = list(iterable)[::-1]
        
        # iterate through list and numerate iterations
        for i, item in enumerate(iterable):
            self._variable.define(context, item)
            context['loop'] = {
                'counter0':     i,
                'counter':      i + 1,
                'revcounter':   len_values - i,
                'revcounter0':  len_values - i - 1,
                'first':        (i == 0),
                'last':         (i == len_values - 1),
                'even':         i % 2 != 0,
                'odd':          i % 2 == 0,
                'length0':      len_values - 1,
                'length':       len_values,
                'parent':       parent,
                '__forloop__':  self
            }
            for node in self._body_loop:
                nodelist.append(node.render(context))
        
        # pop the highest layer in the context
        context.pop()
        if nodelist:
            return nodelist.render(context)
        return self._body_else.render(context)
    
    def __repr__(self):
        return '<ForLoopTag: [%r in %r%s]>' % (
            self._variable,
            self._iterable,
            (self._reversed) and ' reversed' or ''
        ) 

stdlib.register_tag(ForLoopTag)


class RangeLoopTag(Node):
    """
    Range Loop
    ==========
    
    Counts from X to Y, by stepping Z::
    
        {% range var from X to Y step Z %}
            ...
        {% endrange %}
        
    When not defining "step Z" it will assume that step is one.
    
    If you want to cound downwards you can use ``downto``:
    
        {% range var from X downto Y step Z %}
            ...
        {% endrange %}
    """
    
    rules = {
        'inc_default': [
            KeywordNode('range'), VariableNode(), KeywordNode('from'),
            ChoiceNode(), KeywordNode('to'), ChoiceNode()],
        'inc_stepped': [
            KeywordNode('range'), VariableNode(), KeywordNode('from'),
            ChoiceNode(), KeywordNode('to'), ChoiceNode(),
            KeywordNode('step'), ChoiceNode()],
        'dec_default': [
            KeywordNode('range'), VariableNode(), KeywordNode('from'),
            ChoiceNode(), KeywordNode('downto'), ChoiceNode()],
        'dec_stepped': [
            KeywordNode('range'), VariableNode(), KeywordNode('from'),
            ChoiceNode(), KeywordNode('downto'), ChoiceNode(),
            KeywordNode('step'), ChoiceNode()]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        self._variable = handler_args[1]
        self._lbound = handler_args[3]
        self._ubound = handler_args[5]
        if matched_tag in ('inc_stepped', 'dec_stepped'):
            self._step = handler_args[7]
        self._increment = matched_tag[:3] == 'inc'
        self._body = parser.subparse('endrange')
        
    def findnodes(self):
        yield self
        for node in self._body:
            for n in node.findnodes():
                yield n
        
    def render(self, context):
        from jinja.base import NodeList
        nodelist = NodeList()
        
        # find parent loop
        if 'loop' in context:
            parent = context['loop']
        else:
            parent = {}
        
        # resolve bounds and fix stepping depending
        # on possible reverse counting
        if hasattr(self, '_step'):
            step = self._step.resolve(context)
        else:
            step = 1
        lbound = self._lbound.resolve(context)
        ubound = self._ubound.resolve(context)
        if not self._increment:
            step *= -1
            ubound -= 1
        else:
            ubound += 1
            
        # add layer to context
        context.push()
        
        iterable = xrange(lbound, ubound, step)
        len_values = len(iterable)
        for i, item in enumerate(iterable):
            self._variable.define(context, item)
            context['loop'] = {
                'counter0':     i,
                'counter':      i + 1,
                'revcounter':   len_values - i,
                'revcounter0':  len_values - i - 1,
                'first':        (i == 0),
                'last':         (i == len_values - 1),
                'even':         i % 2 != 0,
                'odd':          i % 2 == 0,
                'length0':      len_values - 1,
                'length':       len_values,
                'parent':       parent
            }
            for node in self._body:
                nodelist.append(node.render(context))
        
        # pop highest layer and render nodelist
        context.pop()
        return nodelist.render(context)

    def __repr__(self):
        if self._increment:
            range_type = 'to'
        else:
            range_type = 'downto'
        if hasattr(self, '_step'):
            step = 'step %r' % self._step
        else:
            step = ''
        return '<RangeLoopTag: [%s %s %s %s]>' % (
            self._lbound,
            range_type,
            self._ubound,
            step
        )

stdlib.register_tag(RangeLoopTag)


class RecurseTag(Node):
    """
    Recursion
    =========

    For use with for loops::

        <ul id="menu">
        {% for item in menu %}
            <li><a href="{{ item.href }}">{{ item.caption|escapexml }}</a>
            {% if item.submenu %}
                <ul>
                    {% recurse item.submenu %}
                </ul>
            {% endif %}
            </li>
        {% endfor %}
        </ul>

    And the context would look like this::

        c = Context({
            'menu': [
                dict(
                    caption='Pages',
                    submenu=[
                        dict(href='index.html', caption='Index'),
                        dict(href='downloads.html', caption='Downloads'),
                        dict(
                            caption='Users',
                            submenu=[
                                dict(href='peter.html',
                                     caption='Peter'),
                                dict(href='max.html',
                                     caption='Max'),
                                dict(href='suzan.html',
                                     caption='Suzan')
                            ]
                        ),
                        dict(
                            caption='Files',
                            submenu=[
                                dict(
                                    caption='Images',
                                    submenu=[
                                        dict(href='vienna.html',
                                             caption='Vienna'),
                                        dict(href='roma.html',
                                             caption='Roma'),
                                        dict(href='tokyo.html',
                                             caption='Tokyo')
                                    ]
                                ),
                                dict(
                                    caption='Videos',
                                    submenu=[
                                        dict(href='party.html',
                                             caption='Party')
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                dict(caption='About', href='about.html')
            ]
        })

    The purpose of this tag is that it recuses by calling a given
    loop again with another variable. If you don't want to use
    the current loop you can specify another::

        {% recurse myvariable in loop.parent.parent %}
    """
    rules = {
        'auto': [
            KeywordNode('recurse'), VariableNode()],
        'in': [
            KeywordNode('recurse'), VariableNode(),
            KeywordNode('in'), VariableNode()]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        if matched_tag == 'in':
            self._loop = handler_args[3]
        else:
            self._loop = None
        self._variable = handler_args[1]
        
    def findnodes(self):
        yield self

    def render(self, context):
        try:
            if self._loop is None:
                loop = context['loop']
            else:
                loop = self._loop.resolve(context)
        except:
            raise TemplateRuntimeError, 'recursion over non for loop'
        iterable = self._variable.resolve(context)
        result = loop['__forloop__'].render(context, iterable)
        return result

    def __repr__(self):
        return '<RecurseTag %s recurse %s>' % (
            self._loop,
            self._variable
        )

stdlib.register_tag(RecurseTag)


class CycleTag(Node):
    """
    Cycling
    =======
    
    Cycle among the given strings each time this tag is encountered.

    Within a loop, cycles among the given strings each time through the loop::

        {% for o in some_list %}
            <tr class="{% cycle "row1", "row2" inline %}">
                ...
            </tr>
        {% endfor %}

    You can also cycle into a variable::
    
        {% for o in some_list %}
            {% cycle class through "row1", "row2" %}
            <tr>
                <td class="{{ class }}">...</td>
                <td class="{{ class }}">...</td>
            </tr>
        {% endfor %}

    It's also possible to iterate through an iterable variable::

        {% for item in some_list %}
            <tr style="background-color: {% cycle row_colors inline %}">
                <td>...</td>
                <td>...</td>
            </tr>
        {% endfor %}

    In this example row_colors is a application provided list with the
    following content: ["red", "blue", "green"]...
        
    It's also possible to cycle through a sequence variable. Then each
    cycling will return the next item from the sequence.

    The cycle tag will reset each time the parent loop iterates. If you don't
    want this behaviour add a ``noreset`` to the call::

        {% cycle "row1", "row2" inline noreset %}
    """
    
    rules = {
        'default': [
            KeywordNode('cycle'), VariableNode(), KeywordNode('through'),
            VariableNode()],
        'list_default': [
            KeywordNode('cycle'), VariableNode(), KeywordNode('through'),
            CollectionNode()],
        'inline': [
            KeywordNode('cycle'), VariableNode(), KeywordNode('inline')],
        'list_inline': [
            KeywordNode('cycle'), CollectionNode(), KeywordNode('inline')],
        'default_nr': [
            KeywordNode('cycle'), VariableNode(), KeywordNode('through'),
            VariableNode(), KeywordNode('noreset')],
        'list_default_nr': [
            KeywordNode('cycle'), VariableNode(), KeywordNode('through'),
            CollectionNode(), KeywordNode('noreset')],
        'inline_nr': [
            KeywordNode('cycle'), VariableNode(), KeywordNode('inline'),
            KeywordNode('noreset')],
        'list_inline_nr': [
            KeywordNode('cycle'), CollectionNode(), KeywordNode('inline'),
            KeywordNode('noreset')],
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        if matched_tag in ('default', 'list_default',
                           'default_nr', 'list_default_nr'):
            self._variable = handler_args[1]
            self._iterable = handler_args[3]
        else:
            self._variable = None
            self._iterable = handler_args[1]
        self._reset = matched_tag in ('default', 'list_default',
                                      'inline', 'list_inline')
        self._pos = -1
        self._parent_iter = None

    def reset(self):
        self._pos = -1
        
    def cycle(self, length):
        self._pos += 1
        if self._pos >= length:
            self._pos = 0
        
    def render(self, context):
        if isinstance(self._iterable, list):
            iterable = self._iterable
        else:
            iterable = self._iterable.resolve(context)

        # auto reset cycle on parent loop iteration
        if self._reset:
            if 'loop' in context and context['loop']['parent']:
                parent = context['loop']['parent']
                new_iter = parent['counter0']
                if not self._parent_iter is None and\
                   self._parent_iter != new_iter:
                    self.reset()
                self._parent_iter = new_iter
        
        self.cycle(len(iterable))
        
        # we are working in inline mode
        if self._variable is None:
            return iterable[self._pos].render(context)
        # send output to variable
        self._variable.define(context, iterable[self._pos].resolve(context))
        return ''

    def __repr__(self):
        return '<CycleTag %s through %s>' % (self._variable, self._iterable)
        

stdlib.register_tag(CycleTag)


class FilterTag(Node):
    """
    Filter
    ======
    
    Parse the content and call the registered filters on it::
    
        {% filter | escapexml %}
            <html>
                <head>
                    <title>HTML PAGE</title>
                </head>
            </html>
        {% endfilter %}
    """
    
    rules = {
        'default': [KeywordNode('filter')]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        self._filters = [(f, args[1:][0]) for f, _, args in stack]
        self._body = parser.subparse('endfilter')
        
    def findnodes(self):
        yield self
        for node in self._body:
            for n in node.findnodes():
                yield n
        
    def render(self, context):
        parsed = []
        for node in self._body:
            parsed.append(node.render(context))
        parsed = ''.join(parsed)
        for f, args in self._filters:
            parsed = f(parsed, context, *[arg.resolve(context)
                                          for arg in args])
        return parsed

    def __repr__(self):
        return '<FilterTag: %r>' % self._filters

stdlib.register_tag(FilterTag)


class DefaultFilterTag(Node):
    """
    Default Filter
    ==============
    
    Sets the default filter for variable output::

        {% setfilter | escapexml %}
    
    and to disable it::

        {% setfilter off %}
    """
    
    rules = {
        'default': [KeywordNode('setfilter')],
        'off': [KeywordNode('setfilter'), KeywordNode('off')]
    }

    def __init__(self, parser, matched_tag, handler_args, stack):
        if matched_tag == 'default':
            self._filters = [(f, args[1:][0]) for f, _, args in stack]
        else:
            self._filters = None
        
    def findnodes(self):
        yield self
        
    def render(self, context):
        if self._filters is None:
            context.filters = None
        else:
            context.filters = self._filters

    def __repr__(self):
        return '<DefaultFilterTag: %r>' % self._filters

stdlib.register_tag(DefaultFilterTag)


class ConditionTag(Node):
    """
    Conditions
    ==========
    
    The ``{% if %}`` tag evaluates a variable, and if that variable is "true"
    (i.e. exists, is not empty, and is not a false boolean value) the contents
    of the block are output::

        {% if users_online %}
            We currently have users on this webpage.
        {% else %}
            No users found. stupid -.-
        {% endif %}
    
    As you can see, the ``if`` tag can take an option ``{% else %}`` clause
    that will be displayed if the test fails.
    """
    
    rules = {
        'default': [KeywordNode('if'), ChoiceNode()],
        'negated': [KeywordNode('if'), KeywordNode('not'), ChoiceNode()]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._body_true, self._body_false = parser.forkparse('else', 'endif')
        if matched_tag == 'negated':
            self._variable = handler_args[2]
            self._negated = True
        else:
            self._variable = handler_args[1]
            self._negated = False
        self._filters = [(f, args[1:][0]) for f, _, args in stack]
    
    def findnodes(self):
        yield self
        for node in self._body_true:
            for n in node.findnodes():
                yield n
        for node in self._body_false:
            for n in node.findnodes():
                yield n
    
    def render(self, context):
        if context.filters is None:
            filters = self._filters[:]
        else:
            filters = self._filters + context.filters
        var = self._variable.resolve(context)
        for f, args in filters:
            var = f(var, context, *[arg.resolve(context) for arg in args])
        if self._negated:
            var = not var
        if var:
            return self._body_true.render(context)
        return self._body_false.render(context)
    
    def __repr__(self):
        if self._negated:
            neg = 'not '
        else:
            neg = ''
        return '<ConditionTag %s%s>' % (neg, self._variable)

stdlib.register_tag(ConditionTag)


class ComparisonTag(Node):
    """
    Comparison
    ==========
    
    You can use `equals` to compare two variables::

        {% if variable equals other_variable %}
            ...
        {% endif %}

    or::

        {% if not variable equals other_variable %}
            ...
        {% endif %}
    """
    
    rules = {
        'default': [KeywordNode('if'), ChoiceNode(), KeywordNode('equals'),
                    ChoiceNode()],
        'negated': [KeywordNode('if'), KeywordNode('not'), ChoiceNode(),
                    KeywordNode('equals'), ChoiceNode()]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._body_true, self._body_false = parser.forkparse('else', 'endif')
        self._negated = matched_tag == 'negated'
        self._var1 = handler_args[1 + self._negated]
        self._var2 = handler_args[3 + self._negated]
    
    def findnodes(self):
        yield self
        for node in self._body_true:
            for n in node.findnodes():
                yield n
        for node in self._body_false:
            for n in node.findnodes():
                yield n
    
    def render(self, context):
        var1 = self._var1.resolve(context)
        var2 = self._var2.resolve(context)
        if self._negated:
            test = var1 != var2
        else:
            test = var1 == var2
        if test:
            return self._body_true.render(context)
        return self._body_false.render(context)
    
    def __repr__(self):
        return '<ComparisonTag %s%s equals %s>' % (
            not self._negated and 'not ' or '',
            self._var1,
            self._var2
        )

stdlib.register_tag(ComparisonTag)


class BlockTag(Node):
    """
    Blocks
    ======
    
    Defines a block in a template, a childtemplate can override.
    
    Usage::
    
        {% block "name" %}
            default content
        {% endblock %}
    
    alternative way::
    
        {% marker "name" set "default content" %}
        
    or without default value::
        
        {% marker "name" %}
    """
    
    rules = {
        'standard': [KeywordNode('block'), ValueNode()],
        'default':  [KeywordNode('marker'), ValueNode(), KeywordNode('set'),
                     ValueNode()],
        'marker':   [KeywordNode('marker'), ValueNode()],
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        from jinja.base import NodeList
        self._name = handler_args[1].resolve()
        if matched_tag == 'standard':
            self._body = parser.subparse('endblock')
        elif matched_tag == 'default':
            self._body = handler_args[3]
        else:
            self._body = NodeList()
        
    def findnodes(self):
        yield self
        for node in self._body.findnodes():
            for n in node.findnodes():
                yield n
        
    def replace(self, node):
        if not isinstance(node, BlockTag):
            raise TypeError, 'invalid nodetype %r' % node.__class__
        self._body = node._body
        
    def render(self, context):
        return self._body.render(context)

    def __repr__(self):
        return '<BlockTag %s: %s>' % (self._name, self._body)

stdlib.register_tag(BlockTag)


class PrepareTag(Node):
    """
    Prepare
    =======

    Prepares a block for later usage::

        {% prepare "name" %}
            ...
        {% endprepare %}

    Or with arguments::

        {% prepare "name" accepting text %}
            ...
            {{ text }}
            ...
        {% prepare %}

    You can call those blocks from everywhere using {% call %}::

        {% call "name", "This is an argument" %}

    missing arguments get ignored.
    """
    
    rules = {
        'call':         [KeywordNode('call'), ValueNode(), CollectionNode()],
        'define':       [KeywordNode('prepare'), ValueNode()],
        'ext-define':   [KeywordNode('prepare'), ValueNode(),
                         KeywordNode('accepting'), CollectionNode()]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._name = handler_args[1].resolve()
        if matched_tag == 'call':
            self._call = True
            self._args = handler_args[2]
        else:
            self._call = False
            if matched_tag == 'define':
                self._args = []
            else:
                self._args = handler_args[3]
            self._body = parser.subparse('endprepare')
        
    def findnodes(self):
        yield self
        if not self._call:
            for node in self._body.findnodes():
                for n in node.findnodes():
                    yield n
        
    def render(self, context):
        if not self._call:
            context.registry['prepared', self._name] = (self._body, self._args)
            return ''
        else:
            try:
                body, args = context.registry['prepared', self._name]
            except KeyError:
                raise TemplateRuntimeError, 'callable %r not found' % self._name
            # push the arguments into the context
            context.push()
            for pos, arg in enumerate(args):
                try:
                    value = self._args[pos].resolve(context)
                    arg.define(context, value)
                except IndexError:
                    arg.unset(context)
            result = body.render(context)
            context.pop()
            return result

    def __repr__(self):
        if self._call:
            return '<PrepareTag %s called %s>' % (self._name, self._args)
        return '<PrepareTag %s accepting %s: %s>' % (self._name, self._args,
                                                     self._body)

stdlib.register_tag(PrepareTag)


class ExtendsTag(Node):
    """
    Template Inheritance
    ====================
    
    Template inheritance allows you to build a base "skeleton" template that
    contains all the common elements of your site and defines **blocks** or
    **markers** that child templates can override.
    
    Here a small example for a base template::
    
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
            <link rel="stylesheet" href="style.css" />
            <title>{% marker "title" set "Index" %} - MyWebpage</title>
        </head>
        <body>
            <div id="content">
                {% marker "content" %}
            </div>
            
            <div id="footer>"
                {% block "footer" %}
                copyright 2006 by myself.
                {% endblock %}
            </div>
        </body>
        
    In this example, the ``{% block %}`` and ``{% marker %}`` tags defines
    some blocks that child templates can fill in.
    
    And here a possible child template::
    
        {% extends "base" %}
        {% marker "title" set "Downloads" %}
        {% block "content" %}
            This is the page content.
        {% endblock %}
        
    You can also inherit from this new child template.
    """
    
    rules = {
        'default': [KeywordNode('extends'), ValueNode()]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._name = handler_args[1].resolve()
        # must set _template here because __repr__ uses it when
        # TemplateSyntaxError is raised below
        self._template = '?'
        if not parser.first:
            raise TemplateSyntaxError, 'extends has to be first in template'
        if not hasattr(parser, '_extends'):
            parser._extends = self._name
        else:
            raise TemplateSyntaxError, 'extends called twice'
        load = parser.loader.load_and_compile_uncached
        self._nodelist = parser.parse()
        self._template = load(self._name, parser.library, parser.template_name)
        overwrites = {}
        for node in self._nodelist.get_nodes_by_type(BlockTag):
            overwrites[node._name] = node
        for node in self._template.get_nodes_by_type(BlockTag):
            if node._name in overwrites:
                node.replace(overwrites[node._name])
        
    def findnodes(self):
        for node in self._template.findnodes():
            yield node
        
    def render(self, context):
        return self._template.render(context)

    def __repr__(self):
        return '<ExtendsTag %s: %s>' % (self._name, self._template)

stdlib.register_tag(ExtendsTag)


class IncludeTag(Node):
    """
    Including Templates
    ===================
    
    Using ``{% include %}`` you can load a template and render it with the
    current context. This is a way of "including" other templates within the
    current template::
    
        {% include "header" %}
            this is the current content
        {% include "footer" %}
        
    Normally the use of ``{% extends %}`` is much more flexible but sometimes
    it may be usefull to include a template at a given position.

    You can also use {% require %} which does the same as include but doesn't
    render anything and loads a template only once.
    """
    
    rules = {
        'default': [KeywordNode('include'), ValueNode()],
        'require': [KeywordNode('require'), ValueNode()],
        'require_as': [KeywordNode('require'), ValueNode(), KeywordNode('as'),
                       VariableNode()]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        name = handler_args[1].resolve()
        load = parser.loader.load_and_compile_uncached
        self._name = name
        self._nodelist = load(name, parser.library, parser.template_name)
        self._render = matched_tag == 'default'
        self._dump = matched_tag == 'require_as'
        if (self._dump):
            self._variable = handler_args[3]
        
    def findnodes(self):
        yield self
        for node in self._nodelist:
            for n in node.findnodes():
                yield n
        
    def render(self, context):
        load = ('template', self._name)
        if self._render or not load in context.registry:
            context.registry[load] = True
            result = self._nodelist.render(context)
            if self._render:
                return result
            elif self._dump:
                self._variable.define(context, result)
        return ''

    def __repr__(self):
        return '<IncludeTag %s: %s>' % (self._name, self._nodelist)

stdlib.register_tag(IncludeTag)


class IfChangedTag(Node):
    """
    Ouput if Changed
    ================
    
    Check if a value has changed from the last iteration of a loop.

    The 'ifchanged' block tag is used within a loop. It checks its own
    rendered contents against its previous state and only displays its content
    if the value has changed.
    """
    rules = {
        'default': [KeywordNode('ifchanged')]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._nodelist = parser.subparse('endifchanged')
        self._last = None
        
    def findnodes(self):
        yield self
        for node in self._nodelist:
            for n in node.findnodes():
                yield n
        
    def render(self, context):
        result = self._nodelist.render(context)
        if result != self._last:
            self._last = result
            return result
        return ''

    def __repr__(self):
        return '<IfChangedTag %s>' % (self._nodelist)

stdlib.register_tag(IfChangedTag)


class CaptureTag(Node):
    """
    Capture Output
    ==============
    
    Captures output and stores it in a variable::
    
        {% capture as title %}{% marker "title" %}{% endcapture %}
    
    This allows the double usage of block tags.
    """
    
    rules = {
        'default': [KeywordNode('capture'), KeywordNode('as'), VariableNode()]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._variable = handler_args[2]
        self._body = parser.subparse('endcapture')
        
    def findnodes(self):
        yield self
        for node in self._body:
            for n in node.findnodes():
                yield n
    
    def render(self, context):
        self._variable.define(context, self._body.render(context))
        return ''

    def __repr__(self):
        return '<CaptureTag %s: %s>' % (self._variable, self._body)

stdlib.register_tag(CaptureTag)


class DefineTag(Node):
    """
    Modify / Set Variables
    ======================
    
    Sets an variable.
    
    Usage::
    
        {% define my_variable "Some Value" %}
        
    You can also append filters::
    
        {% define escaped content | escapexml %}
    """
    
    rules = {
        'default': [KeywordNode('define'), VariableNode(), ChoiceNode()]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        self._variable = handler_args[1]
        self._value = handler_args[2]
        self._filters = [(f, args[1:][0]) for f, _, args in stack]
        
    def findnodes(self):
        yield self._variable
        
    def render(self, context):
        value = self._value.resolve(context)
        for f, args in self._filters:
            value = f(value, *[arg.resolve(context) for arg in args])
        self._variable.define(context, value)
        return ''

    def __repr__(self):
        return '<DefineTag %s: %s>' % (self._variable, self._value)

stdlib.register_tag(DefineTag)


class DebugTag(Node):
    """
    Debug Output
    ============
    
    Returns the current context::
    
        {% debug %}
    """
    
    rules = {
        'default': [KeywordNode('debug')]
    }
    
    def __init__(self, parser, matched_tag, handler_args, stack):
        pass
        
    def render(self, context):
        from pprint import pformat
        return pformat(context.dictrepr())

    def __repr__(self):
        return '<DebugTag>'
        
stdlib.register_tag(DebugTag)
