from turbogears.widgets import CSSLink as TGCSSLink, JSLink as TGJSLink
from turbogears import config
from release import version

__all__ = ['JSLink', 'CSSLink', 'YAHOO_YUI_URL']

serve_from_yahoo = config.get('app.yui.serve_from_yahoo', False)
serve_from_yahoo_cn = config.get('app.yui.serve_from_yahoo_cn', False)

if serve_from_yahoo_cn:
    YAHOO_YUI_URL = 'http://cn.yui.yahooapis.com/%s/build/' % version
else:
    YAHOO_YUI_URL = 'http://yui.yahooapis.com/%s/build/' % version

class PlainJSLink(TGJSLink):
    def __init__(self, *args, **kw):
        args = ("", )+args
        super(PlainJSLink, self).__init__(*args, **kw)

    def update_params(self, d):
        super(PlainJSLink, self).update_params(d)
        d['link'] = self.name

class PlainCSSLink(TGCSSLink):
    def __init__(self, *args, **kw):
        args = ("", )+args
        super(PlainCSSLink, self).__init__(*args, **kw)

    def update_params(self, d):
        super(PlainCSSLink, self).update_params(d)
        d['link'] = self.name

# Functions seem to be sufficient as wrappers:
def YUILink(plainClass, tgClass, mod, *args, **kw):
    if serve_from_yahoo:
        lst = list(args)
        lst[0] = YAHOO_YUI_URL + lst[0]
        return plainClass(*tuple(lst), **kw)
    else:
        return tgClass(mod, *args, **kw)

def JSLink(mod, *args, **kw):
    return YUILink(PlainJSLink, TGJSLink, mod, *args, **kw)

def CSSLink(mod, *args, **kw):
    return YUILink(PlainCSSLink, TGCSSLink, mod, *args, **kw)
