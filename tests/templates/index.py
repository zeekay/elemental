from elemental.html import *

def page(name):
    return html(
        head(
            title('hello %s' % name),
            link(rel='stylesheet', href='style.css', type='text/css')
        ),
        body(
            h1('hello %s' % name, cls='default'),
            p('Hey bud, nice to meet you %s!' % name, style='font-size: 1.2em')
        )
    )
