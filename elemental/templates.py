from tags import *
from js import *
from macro import *

class boilerplate(html):
    tag = 'boilerplate'
    format = '''<!doctype html>
<!--[if lt IE 7 ]> <html class="no-js ie6" lang="en"> <![endif]-->
<!--[if IE 7 ]>    <html class="no-js ie7" lang="en"> <![endif]-->
<!--[if IE 8 ]>    <html class="no-js ie8" lang="en"> <![endif]-->
<!--[if (gte IE 9)|!(IE)]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
{children}
</html>'''

    def __init__(self, ga_id='UA-XXXXX-X', jquery_ver='1.6.2',
                 modernizr_ver='2.0.6', head_title='', meta_description='', meta_author=''):
        super(boilerplate, self).__init__()
        self.head(
            meta(charset="utf-8"),
            meta(httpequiv="X-UA-Compatible", content="IE=edge,chrome=1"),
            title(head_title),
            meta(name="description", content=meta_description),
            meta(name="author", content=meta_author),
            meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            link(rel="shortcut icon", href="/favicon.ico"),
            link(rel="stylesheet", href="/css/style.css"),
            modernizr(version=modernizr_ver),
        )
        self.body(
            div(id='container')(
                header(),
                div(id='main', role='main'),
                footer(),
            ),
            jquery(version=jquery_ver),
            pngfix(),
            ga(ga_id),
        )
