from toscawidgets.api import Widget, JSLink, CSSLink

#__all__ = ["Twtools"]

# declare your static resources here

## JS dependencies can be listed at 'javascript' so they'll get included
## before
#my_js = JSLink(modname=__name__, 
#                filename='static/twtools.js', javascript=[])
moo_js    = JSLink(modname=__name__, filename='static/mootools-beta-1.2b2-compatible.js', javascript=[])
moo_js_compressed    = JSLink(modname=__name__, filename='static/mootools-beta-1.2b2-compatible-compressed.js', javascript=[])

my_css = CSSLink(modname=__name__, filename='static/twtools.css')

class MooTools(Widget):
#    template = """<div id="${id}">${value}</div>"""
    template = ""
    ## You can also define the template in a separate package and refer to it
    ## using Buffet style uris
    #template = "toscawidgets.widgets.twtools.templates.twtools"

    javascript = [JSLink(modname=__name__, filename='static/mootools-beta-1.2b2-compatible.js', javascript=[]),
                 ]
    #css = [my_css]

class MooToolsCompressed(Widget):
    javascript = [JSLink(modname=__name__, filename='static/mootools-beta-1.2b2-compatible-compressed.js', javascript=[]),
                 ]


class DomElementWithValue(object):
    def __init__(self, id, value, attrs={}):
        self.id = id
        self.attrs = attrs
        self.value = value
