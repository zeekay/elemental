from collections import deque

class Element(object):
    tag = None
    _format = '<{0}{1}>{2}{3}</{0}>'

    def __init__(self, *args, **attrs):
        self._root = self._parent = None
        elements, self.text = self._parse_args(args)
        self._add_children(elements)
        self.attrs = attrs
        self.__getattribute__ = self.__getattribute

    def __call__(self, *args, **attrs):
        elements, self.text = self._parse_args(args)
        self._add_children(elements)
        self.attrs.update(attrs)
        return self

    def __getattribute(self, name):
        elements = [x for x in self.children if x.tag == name]
        if elements:
            return elements
        else:
            return object.__getattribute__(self, name)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        elif '(' in name:
            return self.__getattribute__(name.split('(')[0])
        else:
            elements = [e for e in self.children if e.tag == name]
            if elements:
                return elements
            if name == 'trait_names': raise AttributeError()
            e = type(name, (Element,), {'tag': name})()
            self._add_tag(name, e)
            return e

    def __setattr__(self, name, item):
        if not name.startswith('_') and isinstance(item, Element):
            self._add_tag(name, item)
        self.__dict__[name] = item

    def __getitem__(self, val):
        if isinstance(val, int):
            return self.children[val]
        if isinstance(val, slice):
            return self.children[val]
        return self._child_query(val)

    def _add_tag(self, tag, e):
        e._parent = self
        e._root = self._root or self
        e._update_children()
        self.__dict__[tag] = e
        for c in self.children:
            if c.tag == e.tag:
                self.children.remove(c)
        self.children.append(e)

    def _update_children(self):
        for e in self._find_children():
            e._root = self._root or self

    def __str__(self):
        return self.render_this()

    def __repr__(self):
        return '<Elemental.{0} object `{1}` at {2}>'.format(self.tag, self.text, hex(id(self)))

    def find_elements(self, path, elements):
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

    def _find_children(self):
        return sum([self.children] + [e._find_children() for e in self.children], [])

    def _child_query(self, val):
        if val.startswith('//'):
            return self.find_elements(val.strip('/'), self._find_children())
        paths = val.strip('/').split('/')
        paths = deque(paths)
        elements = self.children
        while paths:
            elements = self.find_elements(paths.popleft(), elements)
            if not elements: break
        return elements

    def _parse_args(self, args):
        elements, text = [], ''
        for arg in args:
            if isinstance(arg, basestring):
                text = arg
            else: elements.append(arg)
        return elements, text

    def _add_children(self, elements):
        for e in elements:
            if e._root and e._root not in self.children:
                self.children.append(e._root)
                e._root._root = self._root or self
                e._root._parent = self
                e._root._update_children()
            else:
                self.children.append(e)
                e._root = self._root or self
                e._parent = self
                e._update_children()

    def render_attrs(self):
        def map_attr(name):
            return {
                'cls': 'class',
            }.get(name, name)

        attrs = ['='.join([map_attr(k), '"%s"' % v]) for k,v in self.attrs.iteritems()]
        out = ' '.join(attrs)
        return ' %s' % out if out else ''

    def render(self, format=None, this=False):
        if this is False:
            if self._root:
                return self._root.render(format)
        if format is None:
            format = self._format
        return format.format(self.tag,
                             self.render_attrs(),
                             self.text,
                             ''.join(e.render(this=True) for e in self.children))

    def render_this(self, format=None):
        return self.render(format, this=True)

    def clear(self):
        tags = set(e.tag for e in self.children)
        for tag in tags:
            delattr(self, tag)
        self.children = []

    def pop(self):
        if self._parent:
            self._parent.children.remove(self)
            if len([e for e in self._parent.children if e.tag == self.tag]) == 0:
                try:
                    delattr(self._parent, self.tag)
                except AttributeError: pass
        for e in self._find_children():
            e._root = self
        self._root = self._parent = None
        return self
        


class HashedDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class Template(object):
    cache = {}

    def __init__(self, path='templates', debug=False):
        import os, sys, types
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
