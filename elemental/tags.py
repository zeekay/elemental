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
    format = '<{tag}{attrs}>'


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

    def __call__(self, href, *args, **kwargs):
        self.attrs['href'] = href
        super(css, self).__call__(*args, **kwargs)


class js(script):
    def __init__(self, src=None, *args, **kwargs):
        super(js, self).__init__(*args, **kwargs)
        if src:
            self.attrs['src'] = src

    def __call__(self, src, *args, **kwargs):
        self.attrs['src'] = src
        super(js, self).__call__(*args, **kwargs)


class pngfix(Element):
    tag = 'pngfix'
    format = '''<!--[if lt IE 7 ]>
    <script src="js/libs/dd_belatedpng.js"></script>
    <script>DD_belatedPNG.fix("img, .png_bg");</script>
  <![endif]-->'''


class ga(Element):
    tag = 'ga'
    format = '''<script>
    var _gaq=[["_setAccount","{text}"],["_trackPageview"]];
    (function(d,t){{var g=d.createElement(t),s=d.getElementsByTagName(t)[0];g.async=1;
    g.src=("https:"==location.protocol?"//ssl":"//www")+".google-analytics.com/ga.js";
    s.parentNode.insertBefore(g,s)}}(document,"script"));
  </script>'''


class jquery(Element):
    tag = 'jquery'
    format = '<script src="//ajax.googleapis.com/ajax/libs/jquery/{text}/jquery.js"></script>'


class boilerplate(html):
    tag = 'boilerplate'
    format = '''<!doctype html>
<!--[if lt IE 7 ]> <html class="no-js ie6" lang="en"> <![endif]-->
<!--[if IE 7 ]>    <html class="no-js ie7" lang="en"> <![endif]-->
<!--[if IE 8 ]>    <html class="no-js ie8" lang="en"> <![endif]-->
<!--[if (gte IE 9)|!(IE)]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
{children}
</html>'''

    def __init__(self, ga_id='UA-XXXXX-X', jquery_version='1.5.1', description='', author=''):
        super(boilerplate, self).__init__()
        self.head(
            meta(charset="utf-8"),
            meta(httpequiv="X-UA-Compatible", content="IE=edge,chrome=1"),

            title(),
            meta(name="description", content=description),
            meta(name="author", content=author),

            meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            link(rel="shortcut icon", href="/favicon.ico"),

            link(rel="stylesheet", href="css/style.css"),
            script(src="js/libs/modernizr-1.7.min.js"),
        )
        self.body(
            div(id='container')(
                header(),
                div(id='main', role='main'),
                footer(),
            ),
            jquery(jquery_version),
            pngfix(),
            ga(ga_id),
        )

# clean up
del e
del elements
del modules
del Element
