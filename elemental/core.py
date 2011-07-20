import os, sys, types
from collections import deque

try: from lxml.html import fromstring, tostring
except ImportError: fromstring = tostring = None


class Element(object):
    tag = None
    format = '<{tag}{attrs}>{text}{children}</{tag}>'

    def __init__(self, *args, **attrs):
        self._root = self._parent = None
        self.children = []
        elements, self.text = self._parse_args(args)
        self._add_children(elements)
        self.attrs = attrs
        self.__getattribute__ = self.__getattribute

    def __call__(self, *args, **attrs):
        elements, self.text = self._parse_args(args)
        self._add_children(elements)
        self.attrs.update(attrs)
        return self

    def __getattribute(self, attr):
        elements = [x for x in self.children if x.tag == attr]
        if elements:
            return elements
        else:
            return object.__getattribute__(self, attr)

    def __getattr__(self, attr):
        if attr.startswith('_') or attr == 'trait_names':
            raise AttributeError()
        elif '(' in attr:
            return self.__getattribute__(attr.split('(')[0])
        else:
            elements = [e for e in self.children if e.tag == attr]
            if elements:
                return elements
            if attr in self.valid_tags:
                e = self.valid_tags[attr]()
                self._add_child(e)
                return e
            raise InvalidElement(attr)

    def __setattr__(self, attr, item):
        if not attr.startswith('_') and isinstance(item, Element):
            for c in self.children:
                if c.tag == e.tag:
                    self.children.remove(c)
            self._add_child(item)
        self.__dict__[attr] = item

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.children[key]
        if isinstance(key, slice):
            return self.children[key]
        return self.select(key)

    def __str__(self):
        return self.render_this(pretty=True)

    def __repr__(self):
        name = '`%s` ' % self.text[:20] if self.text else ''
        return '<Element.{0} object {1}at {2}>'.format(self.tag, name, hex(id(self)))

    def _parse_args(self, args):
        elements, text = [], ''
        for arg in args:
            if isinstance(arg, basestring):
                text = arg
            else: elements.append(arg)
        return elements, text

    def _add_child(self, e):
        e._parent, e._root = self, self._root or self
        e._update_children()
        self.__dict__[e.tag] = e
        self.children.append(e)

    def _add_children(self, elements):
        for e in elements:
            if e._root and e._root not in self.children:
                e = e._root
            self._add_child(e)

    def _get_children(self):
        return sum([self.children] + [e._get_children() for e in self.children], [])

    def _update_children(self):
        for e in self._get_children():
            e._root = self._root or self

    def _search_elements(self, path, elements):
        if '[' in path:
            tag, path = path[:-1].split('[')
            elements = [e for e in elements if e.tag == tag]
            if not elements:
                return []
        if '=' in path:
            k, v = path.split('=')
            if k == 'text':
                v = v.lower()
                return [e for e in elements if v in e.text.lower()]
            return [e for e in elements if e.attrs.get(k) == v]
        return [e for e in elements if e.tag == path]

    def select(self, query):
        if query.startswith('//'):
            return self._search_elements(query.strip('/'), self._get_children())
        paths = query.strip('/').split('/')
        paths = deque(paths)
        elements = self.children
        while paths:
            elements = self._search_elements(paths.popleft(), elements)
            if not elements: break
        return elements

    def render_attrs(self):
        def map_attr(name):
            return {
                'cls': 'class',
                'httpequiv': 'http-equiv',
            }.get(name, name)

        attrs = ['='.join([map_attr(k), '"%s"' % v]) for k,v in self.attrs.iteritems()]
        out = ' '.join(attrs)
        return ' %s' % out if out else ''

    def render(self, format=None, this=False, pretty=False):
        if this is False and self._root:
            return self._root.render(format)
        format = format or self.format
        out = format.format(tag=self.tag,
                            attrs=self.render_attrs(),
                            text=self.text,
                            children=''.join(e.render_this() for e in self.children))
        if pretty and tostring:
            return prettify(out)
        return out

    def render_this(self, format=None, pretty=False):
        return self.render(format=format, pretty=pretty, this=True)

    def clear(self):
        tags = set(e.tag for e in self.children)
        for tag in tags:
            delattr(self, tag)
        self.children = []

    def pop(self):
        if self._parent:
            self._parent.children.remove(self)
            if [e for e in self._parent.children if e.tag == self.tag]:
                try: delattr(self._parent, self.tag)
                except AttributeError: pass
        for e in self._get_children():
            e._root = self
        self._root = self._parent = None
        return self

    @property
    def valid_tags(self):
        if not hasattr(Element, '_valid_tags'):
            tags = __import__('elemental.tags', fromlist=['tags'])
            Element._valid_tags = dict((x, getattr(tags, x)) for x in dir(tags) if not x.startswith('_'))
        return self._valid_tags


class HashedDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class Template(object):
    cache = {}

    def __init__(self, path='templates', debug=False):
        self.debug = debug
        sys.path.insert(0, os.path.abspath(path))

    def __call__(self, path, *args, **kwargs):
        self.path = path
        if path in Template.cache and not self.debug:
            template = Template.cache[path]
        else:
            template = self.load_template(path)
            Template.cache[path] = template
        return self.render(template, *args, **kwargs)

    def load_template(self, path):
        try:
            mod, template = path.rsplit('.', 1)
            mod = __import__(mod, fromlist=[template])
            template = getattr(mod, template)
            if isinstance(template, types.ModuleType):
                template = getattr(template, 'page')
        except:
            mod = __import__(path)
            template = getattr(mod, 'page')
        return template

    def render(self, template, *args, **kwargs):
        signature = (self.path, args, HashedDict(kwargs))
        if signature in Template.cache and not self.debug:
            return Template.cache[signature]
        rendered = template(*args, **kwargs).render()
        Template.cache[signature] = rendered
        return rendered


class InvalidElement(Exception):
   def __init__(self, value):
       self.parameter = value

   def __str__(self):
       return repr(self.parameter)


def prettify(out):
    if out.startswith('<!') and '<head' in out:
        doctype, head, body = out.partition('<head')
        body = ''.join(['<html>', head, body])
        _, head, body = tostring(fromstring(out), pretty_print=True).partition('<head')
        return ''.join([doctype, head, body])
    return tostring(fromstring(out), pretty_print=True)
