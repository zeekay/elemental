from sys import modules
from core import Element

class HtmlElement(Element):
    attr_remap = {
        'cls': 'class',
    }

elements = [
    'html', 'head', 'body', 'div', 'p', 'a', 'img', 'h1', 'h2', 'h3', 'h4', 'h5',
    'code', 'pre', 'ul', 'li', 'title', 'span', 'style', 'script', 'table',
    'thead', 'tr', 'th', 'td', 'canvas', 'audio', 'video',
    'section', 'article', 'header', 'footer', 'figure', 'em'
]

for e in elements:
    setattr(modules[__name__], e, type(e, (HtmlElement,), {'tag': e}))

class comment(HtmlElement):
    tag = 'comment'
    format = '<!-- {text} -->'

class doctype(HtmlElement):
    tag = 'doctype'
    format = '<!{tag} {text}{attrs}>{children}'


class link(HtmlElement):
    tag = 'link'
    format = '<{tag}{attrs}>'


class meta(link):
    tag = 'meta'
