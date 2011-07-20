import os, sys, types

class Element(object):
    tag = None
    format = '<{0}{1}>{2}{3}</{0}>'

    def __init__(self, *args, **attrs):
        self.children, self.text = self._parse_args(args)
        self.attrs = attrs

    def __call__(self, *args, **attrs):
        elements, text = self._parse_args(args)
        self.text = text
        self.children.extend(elements)
        self.attrs.update(attrs)
        return self

    def _parse_args(self, args):
        elements, text = [], ''
        for arg in args:
            if isinstance(arg, basestring):
                text = arg
            else: elements.append(arg)
        return elements, text

    def render_attrs(self):
        def map_attr(name):
            return {
                'cls': 'class',
            }.get(name, name)

        attrs = ['='.join([map_attr(k), '"%s"' % v]) for k,v in self.attrs.iteritems()]
        out = ' '.join(attrs)
        return ' %s' % out if out else ''

    def render(self, format=None):
        if format is None:
            format = self.format
        return format.format(self.tag,
                             self.render_attrs(),
                             self.text,
                             ''.join(e.render() for e in self.children))

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
