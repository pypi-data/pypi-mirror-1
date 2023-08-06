from tw.api import Widget, JSLink, CSSLink, CSSSource
from genshi.template.text import TextTemplate
import tw.forms

from tw.mootools.base import moo_core_js_compressed, moo_more_js_compressed

# declare your static resources here
omnigrid_js = JSLink(modname=__name__, filename='static/omnigrid/omnigrid11.js', javascript=[])
omnigrid_css = CSSLink(modname=__name__, filename='static/omnigrid/omnigrid.css', javascript=[])

class SimpleGridWidget(tw.forms.datagrid.DataGrid):
    ## You can also define the template in a separate package and refer to it
    ## using Buffet style uris
    template = "genshi:tw.mootools.templates.simplegrid"

    javascript = [moo_core_js_compressed, moo_more_js_compressed, omnigrid_js]
    css = [omnigrid_css]
    
