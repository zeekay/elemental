from core import *

elements = ['html', 'head', 'body', 'a', 'p', 'h1', 'h2', 'h3', 'div', 'ul', 'li', 'title', 'link', 'script']
for e in elements:
    setattr(sys.modules[__name__], e, type(e, (Element,), {'tag': e}))
