from core import Element


class html5(Element):
    tag = 'html5'
    html_attrs = {}

    @property
    def format(self):
        return '<!doctype html><html%s>{children}</html>' % \
            (' ' + self.render_attrs(self.html_attrs) if self.html_attrs else '',)


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


class js(Element):
    tag = 'js'

    @property
    def format(self):
        return '<script src={text}></script>' if text.startswith('//:') else '<script>{text}</script>'


class css(Element):
    tag = 'css'
    format = '<link rel="stylesheet"{attrs} href="{text}">'
