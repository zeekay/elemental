from sys import modules
from core import Element as _Element

_cdnjs_url = '<script src="//cdnjs.cloudflare.com/ajax/libs/{0}.js"></script>'

_cdnjs = [x.split() for x in """
xuijs 2.0.0 xui.min.js
css3finalize 1.43 jquery.css3finalize.min.js
processing.js 1.2.1 processing-api.min.js
prototype 1.7.0.0 prototype.js
camanjs 2.2 caman.full.min.js
noisy 1.0 jquery.noisy.min.js
modernizr 2.0.6 modernizr.min.js
string_score 0.1.10 string_score.min.js
mustache.js 0.3.0 mustache.min.js
dojo 1.6.0 dojo.xd.js
ext-core 3.1.0 ext-core.js
sizzle 1.4.4 sizzle.min.js
graphael 0.4.1 g.raphael-min.js
ocanvas 1.0 ocanvas.min.js
jqueryui 1.8.13 jquery-ui.min.js
spinejs 0.0.4 spine.min.js
galleria 1.2.3 galleria.min.js
less.js 1.1.3 less-1.1.3.min.js
underscore.js 1.1.7 underscore-min.js
highcharts 2.1.6 highcharts.js
flexie 1.0.0 flexie.min.js
waypoints 1.1 waypoints.min.js
yepnope 1.0.1 yepnope.min.js
mootools 1.3.2 mootools-yui-compressed.js
script.js 1.3 script.min.js
handlebars.js 1.0.0.beta2 handlebars.min.js
json2 20110223 json2.js
cufon 1.09i cufon-yui.js
zepto 0.6 zepto.min.js
chrome-frame 1.0.2 CFInstall.min.js
selectivizr 1.0.2 selectivizr-min.js
sammy.js 0.6.3 sammy.min.js
es5-shim 1.2.4 es5-shim.min.js
js-signals 0.6.1 js-signals.min.js
raphael 1.5.2 raphael-min.js
yui 3.3.0 yui-min.js
underscore.string 1.1.4 underscore.string.min.js
labjs 2.0 LAB.min.js
jquery 1.6.2 jquery.min.js
pubnub 3.1.2 pubnub.min.js
backbone.js 0.5.1 backbone-min.js
twitterlib.js 0.9.0 twitterlib.min.js
scriptaculous 1.8.3 scriptaculous.js
headjs 0.96 head.min.js
webfont 1.0.19 webfont.js
require.js 0.24.0 require.min.js
socket.io 0.7.0 socket.io.min.js
knockout 1.2.1 knockout-min.js
""".splitlines() if x]

for _name, _version, _filename in _cdnjs:
    _tag = _name.replace('.','')
    _dict = {'tag': _tag,
             'format': _cdnjs_url.format('%s/{text}/{%s}' % (_name, _filename)),
             'version': _version}
    setattr(modules[__name__], _tag, type(_tag, (_Element,), _dict))

def _get_latest_cdnjs():
    import requests
    import json
    data = requests.get('http://www.cdnjs.com/packages.json').read()
    packages = json.loads(data)['packages']
    for n, v, f in [(x['name'], x['version'], x['filename']) for x in packages if x]:
        print n, v, f


class jquery(_Element):
    tag = 'jquery'
    format = '<script src="http://ajax.googleapis.com/ajax/libs/jquery/{text}/jquery.min.js"></script>'
