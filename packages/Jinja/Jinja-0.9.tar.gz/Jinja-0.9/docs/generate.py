# -*- coding: utf-8 -*-
"""
    Jinja Documenation Builder
"""
import sys
import os
import re
from docutils import nodes, utils
from docutils.core import publish_parts
from docutils.writers import html4css1
from xml.sax import saxutils
from jinja import Template, Context, StringLoader

TEMPLATE = """
<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{{ title }} | Jinja Documentation</title>
    <style text="text/css">
        body {
            font-family: 'Arial', sans-serif;
            margin: 1em;
            padding: 0;
        }

        #navigation {
            float: right;
            margin: -1em -1em 1em 1em;
            padding: 1em 2em 0 2em;
            border: 1px solid #bbb;
            border-width: 0 0 1px 1px;
            background-color: #f8f8f8;
        }

        #page {
            width: 45em;
        }

        a {
            color: #d00;
        }

        a:hover {
            color: #d40;
        }

        h1 {
            font-size: 2em;
            color: #d00;
            margin: 0.5em 0 0.5em 0;
            padding: 0;
        }

        h2 {
            font-size: 1.7em;
            color: #bd2121;
            margin: 1em 0 0.5em 0;
        }

        h3 {
            font-size: 1.3em;
            color: #8a2424;
            margin: 0.5em 0 0 0;
        }

        p {
            margin: 0.5em 1em 0.5em 1em;
        }

        pre {
            margin: 1em 0 1em 2em;
            padding: 0.5em;
            border-top: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            background-color: #f2f2f2;
            overflow: auto;
        }
        
        li {
            line-height: 1.4em;
        }
        
        hr {
            margin: 1em;
            padding: 0;
            height: 1px!important;
            background-color: #ccc;
            border: none!important;
        }
        
        div.admonition {
            margin: 1em 0 1em 1.5em;
            padding: 0.5em 0.5em 0.5em 2em;
            background-color: #f6e3e3;
            border: 1px solid #d50000;
            border-left: none;
            border-right: none;
        }
        
        div.admonition p.admonition-title {
            font-size: 1.1em;
            color: #d40;
            font-weight: bold;
            margin: 0 0 0.5em -1em;
        }
        
        table {
            border-collapse: collapse;
            margin: 1em 2em 1em 1.5em;
        }
        
        table td, table th {
            text-align: left;
            border: 1px solid #eee;
            padding: 0.3em;
        }
        
        table th {
            background-color: #d00000;
            color: white;
            border: 1px solid #d00000;
            border-bottom: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div id="navigation">
        <h3>Documentation</h3>
        <ul>
            {% if not root %}
            <li><a href="index.html">back to index</a></li>
            {% endif %}
            <li><a href="http://wsgiarea.pocoo.org/repos/jinja/trunk/docs/source/{{ fid }}.txt">view source online</a></li>
        </ul>
        {% if toc %}
            <h3>Table of Contents</h3>
            <ul>
            {% for item in toc %}
                <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
            {% endfor %}
            </ul>
        {% endif %}
    </div>
    <h1>{{ title }}</h1>
    <div id="page">
        {{ body }}
    </div>
</body>
</html>
"""[1:]

class DocumentationBuilder(object):

    def __init__(self, root, dest, rules):
        self.root = root
        self.rules = rules
        self.dest = dest
            
    def build(self):
        for folder, subfolders, files in os.walk(self.root):
            searchpath = []
            if '.svn' in subfolders:
                subfolders.remove('.svn')
            for f in files:
                f = os.path.join(folder, f)[len(self.root):]
                for rule, params in self.rules:
                    m = rule.search(f)
                    if m is None:
                        continue
                    fid = f.rsplit('/', 1)[-1].rsplit('.')[0]
                    output = self.render(fid, f, params)
                    self.save(fid, f, output, params)
                    break
                
    def render(self, fid, f, params):
        writer = PageWriter()
        parts = publish_parts(
            file(os.path.join(self.root, f)).read(),
            source_path=f,
            writer=writer,
            settings_overrides={'initial_header_level': 2}
        )
        template = Template(TEMPLATE, StringLoader())
        return template.render(Context({
            'title': parts['title'],
            'body': parts['body'],
            'toc': parts['toc'],
            'root': fid == 'index',
            'fid': fid
        })).encode('utf-8')
        
    def save(self, fid, f, output, params):
        folder = os.path.join(self.dest, params.get('dest', ''))
        filename = '%s.html' % fid
        try:
            os.makedirs(folder)
        except OSError:
            pass
        fp = file(os.path.join(folder, filename), 'w')
        fp.write(output)
        fp.close()


class PageWriter(html4css1.Writer):
    
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = PageTranslator

    def translate(self):
        html4css1.Writer.translate(self)
        contents = self.build_contents(self.document)
        contents_doc = self.document.copy()
        contents_doc.children = contents
        contents_visitor = self.translator_class(contents_doc)
        contents_doc.walkabout(contents_visitor)

        toc = []
        tmp = {}
        for item in contents_visitor.fragment:
            if not item or item in ('<li>', '</li>'):
                continue
            elif item.startswith('<a class="reference" '):
                tmp['href'] = re.search('href="(.*?)"', item).group(1)
            elif item == '</a>':
                toc.append(tmp)
                tmp = {}
            else:
                tmp['caption'] = item 
        self.parts['toc'] = toc

    def build_contents(self, node, level=0):
        level += 1
        sections = []
        i = len(node) - 1
        while i >= 0 and isinstance(node[i], nodes.section):
            sections.append(node[i])
            i -= 1
        sections.reverse()
        entries = []
        autonum = 0
        depth = 4   # XXX FIXME
        for section in sections:
            title = section[0]
            entrytext = title
            try:
                reference = nodes.reference('', '', refid=section['ids'][0], *entrytext)
            except IndexError:
                continue
            ref_id = self.document.set_id(reference)
            entry = nodes.paragraph('', '', reference)
            item = nodes.list_item('', entry)
            if level < depth:
                subsects = self.build_contents(section, level)
                item += subsects
            entries.append(item)
        if entries:
            contents = nodes.bullet_list('', *entries)
            return contents
        else:
            return []

class PageTranslator(html4css1.HTMLTranslator):
    
    def visit_table(self, node):
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))
    
    def visit_reference(self, node):
        if node.has_key('refuri'):
            href = node['refuri']
            if ( self.settings.cloak_email_addresses
                 and href.startswith('mailto:')):
                href = self.cloak_mailto(href)
                self.in_mailto = 1
        else:
            assert node.has_key('refid'), \
                   'References must have "refuri" or "refid" attribute.'
            href = '#' + node['refid']
        if not '/' in href and href.endswith('.txt'):
            href = './%s.html' % (href[:-4])
        atts = {'href': href, 'class': 'reference'}
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        self.body.append(self.starttag(node, 'a', '', **atts))


if __name__ == '__main__':
    app = DocumentationBuilder(
        'source/', 'build/', [
            (re.compile(r'\.txt$'), {
                'dest':     './',
                'root':     './'
            })
        ]
    )
    app.build()
