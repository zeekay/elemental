from sys import modules
from core import Element

elements = [
    # general
    'html', 'head', 'body', 'div', 'p', 'a', 'img',
    'h1', 'h2', 'h3', 'h4', 'h5', 'code', 'obj',
    'ul', 'li', 'title', 'span', 'pre', 'style',
    'script', 'noscript',
    # table
    'table', 'thead', 'tr', 'th', 'td',
    # html5 
    'canvas', 'audio', 'video',
    # semantic
    'section', 'article', 'header', 'footer', 'figure', 'em'
]

for e in elements:
    setattr(modules[__name__], e, type(e, (Element,), {'tag': e}))

class doctype(Element):
    tag = 'doctype'
    format = '<!{tag} {text}{attrs}>{children}'

class link(Element):
    tag = 'link'
    format = '<{tag}{attrs} />'

class meta(link):
    tag = 'link'

class html5(Element):
    tag = 'html5'
    html_attrs = {}

    @property
    def format(self):
        return '<!doctype html><html%s>{children}</html>' % \
                   (' ' + self.render_attrs(self.html_attrs) if self.html_attrs else '',)

# clean up
del e
del elements
del modules
del Element
