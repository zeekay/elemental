from collections import deque

class Element(object):
    tag = None
    _format = '<{0}{1}>{2}{3}</{0}>'

    def __init__(self, *args, **attrs):
        self._parent = None
        self.tag = type(self).tag
        self.format = type(self)._format
        elements, self.text = self._parse_args(args)
        self.children = self._get_children(elements)
        self.attrs = attrs
        self.__getattribute__ = self.__getattribute

    def __call__(self, *args, **attrs):
        elements, self.text = self._parse_args(args)
        self.children.extend(self._get_children(elements))
        self.attrs.update(attrs)
        return self

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
            cls = type(name, (Element,), {'tag': name, '_parent': self._parent or self})
            e = cls()
            self.children.append(e)
            setattr(self, name, e)
            return e

    def __getattribute(self, name):
        elements = [x for x in self.children if x.tag == name]
        if elements:
            return elements
        else:
            return object.__getattribute__(self, name)

    def __getitem__(self, val):
        if isinstance(val, int):
            return self.children[val]
        if isinstance(val, slice):
            return self.children[val]
        return self._child_query(val)

    def __str__(self):
        return '<Elemental.{0} object `{1}` at {2}>'.format(self.tag, self.text, hex(id(self)))

    def __repr__(self):
        return self.__str__()

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
        return [e for e in elements if e.tag == val]

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

    def _get_children(self, elements):
        children = []
        for e in elements:
            if e._parent and e._parent not in children:
                children.append(e._parent)
            else:
                children.append(e)
            e._update_parent(self)
        return children

    def _update_parent(self, parent):
        self._parent = parent
        for e in self.children:
            e._update_parent(parent)

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
            if self._parent:
                return self._parent.render(format)
        if format is None:
            format = self._format
        return format.format(self.tag,
                             self.render_attrs(),
                             self.text,
                             ''.join(e.render(this=True) for e in self.children))

    def render_this(self, format=None):
        return self.render(format, this=True)

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
