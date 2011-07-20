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

class css(link):
    def __init__(self, href=None, *args, **kwargs):
        super(css, self).__init__(*args, **kwargs)
        self.attrs['rel'] = 'stylesheet'
        if href:
            self.attrs['href'] = href
        self.attrs['type'] = 'text/css'

    def __call__(self, href, *args, **kwargs):
        self.attrs['href'] = href
        super(css, self).__call__(*args, **kwargs)

class js(script):
    def __init__(self, src=None, *args, **kwargs):
        super(js, self).__init__(*args, **kwargs)
        if src:
            self.attrs['src'] = src
        self.attrs['type'] = 'text/javascript'

    def __call__(self, src, *args, **kwargs):
        self.attrs['src'] = src
        super(js, self).__call__(*args, **kwargs)

# clean up
del e
del elements
del modules
del Element
