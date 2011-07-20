from sys import modules as _m
from core import Element as _E

_elements = ['html', 'head', 'body', 'a', 'p', 'h1', 'h2', 'h3', 'div', 'ul', 'li', 'title', 'link', 'script']
for _e in _elements:
    setattr(_m[__name__], _e, type(_e, (_E,), {'tag': _e}))
