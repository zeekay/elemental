import os, sys, types


class Loader(object):
    cache = {}

    def __init__(self, path='templates', debug=False):
        self.debug = debug
        sys.path.insert(0, os.path.abspath(path))

    def __call__(self, path, *args, **kwargs):
        if path in self.cache and not self.debug:
            template = Loader.cache[path]
        else:
            template = self.load_template(path)
            self.cache[path] = template
        return template(*args, **kwargs).render()

    def load_template(self, path):
        try:
            mod, template = path.rsplit('.', 1)
            mod = __import__(mod, fromlist=[template])
            template = getattr(mod, template)
            if isinstance(template, types.ModuleType):
                template = getattr(template, 'template')
        except:
            mod = __import__(path)
            template = getattr(mod, 'template')
        return template


class CachedLoader(Loader):
    def __call__(self, path, *args, **kwargs):
        if path in self.cache and not self.debug:
            template, fmt_args, fmt_kwargs = self.cache[path]
        else:
            template = self.load_template(path)
            fmt_args, fmt_kwargs = self._format_args(*args, **kwargs)
            template = template(*fmt_args, **fmt_kwargs).render()
            self.cache[path] = template, fmt_args, fmt_kwargs
        return template.format(*args, **kwargs)

    def _format_args(self, *args, **kwargs):
        return tuple('{%s}' % x for x in range(len(args))), dict((x, '{%s}' % x) for x in kwargs)


class RenderLoader(Loader):
    def __call__(self, path, timeout=60, *args, **kwargs):
        signature = (self.path, args, HashedDict(kwargs))
        if signature in self.cache and not self.debug:
            cached = self.cache[signature]
        else:
            template = self.load_template(path)
            cached = template(*args, **kwargs).render()
            self.cache[signature] = cached
        return cached

    def render(self, template, *args, **kwargs):
        if signature in Template.cache and not self.debug:
            return Template.cache[signature]
        rendered = template(*args, **kwargs).render()
        Template.cache[signature] = rendered
        return rendered


class HashedDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

cached = CachedLoader()
debug = Loader(debug=True)
template = Loader()
render = RenderLoader()

