from collections import deque

try:
    from lxml.html import fromstring, tostring
    import difflib
except ImportError: fromstring = tostring = None


class Element(object):
    tag = None
    format = '<{tag}{attrs}>{text}{children}</{tag}>'
    attr_remap = {}

    def __init__(self, *args, **kwargs):
        self._root = self._parent = None
        self.attrs, self.children = {}, []
        attrs, elements, self.text = self._parse_args(args)
        if attrs: self.attrs.update(attrs)
        if kwargs: self.attrs.update(kwargs)
        if elements: self._add_children(elements)
        self.__getattribute__ = self.__getattribute

    def __call__(self, *args, **kwargs):
        attrs, elements, text = self._parse_args(args)
        if attrs: self.attrs.update(attrs)
        if kwargs: self.attrs.update(kwargs)
        if elements: self._add_children(elements)
        if text: self.text = text
        return self

    def __getattribute(self, attr):
        elements = [x for x in self.children if x.tag == attr]
        if elements: return elements
        else: return object.__getattribute__(self, attr)

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
        return self.render(pretty=True, this=True)

    def __repr__(self):
        name = '`%s` ' % self.text[:20] if self.text else ''
        return '<Element.{0} object {1}at {2}>'.format(self.tag, name, hex(id(self)))

    def _parse_args(self, args):
        attrs, elements, text = {}, [], ''
        for arg in args:
            if issubclass(type(arg), Element):
                elements.append(arg)
            elif isinstance(arg, dict):
                attrs.update(arg)
            elif hasattr(arg, '__iter__'):
                for e in arg:
                    # try to instantiate object in case we are passed a class
                    elements.append(e())
            else:
                text = arg
        return attrs, elements, text

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
        attrs = ['='.join([self.attr_remap.get(k, k), '"%s"' % v]) for k,v in self.attrs.iteritems()]
        out = ' '.join(attrs)
        return ' %s' % out if out else ''

    def render(self, pretty=False, this=False):
        if self._root and not this:
            return self._root.render(pretty)
        return prettify(self.render_this()) if pretty and tostring else self.render_this()
    
    def render_children(self):
        return ''.join(e.render_this() for e in self.children)

    def render_this(self):
        return self.format.format(
            tag=self.tag,
            attrs=self.render_attrs(),
            text=self.text,
            children=self.render_children(),
        )

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


class InvalidElement(Exception):
   def __init__(self, value):
       self.parameter = value

   def __str__(self):
       return repr(self.parameter)


def prettify(orig):
    """user lxml's pretty_print feature but only insert whitespace"""
    pretty = tostring(fromstring(orig), pretty_print=True)
    opcodes = (x for x in difflib.SequenceMatcher(None, orig, pretty, autojunk=False).get_opcodes() if x[0] == 'insert')
    offset = 0
    for _, a1, a2, b1, b2 in opcodes:
        chars = pretty[b1:b2]
        # lxml has a habit of fucking shit up so make sure we're only inserting whitespace
        if not chars.strip():
            orig = ''.join([orig[:a1+offset], chars, orig[a2+offset:]])
        offset += b2 - b1
    return orig
