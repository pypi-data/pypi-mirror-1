from tw.api import Widget, JSLink, CSSLink, CSSSource
from genshi.template.text import TextTemplate
import tw.forms

from tw.mootools.base import moo_core_js_compressed, moo_more_js_compressed
from tw.forms import TextArea
from tw.forms.validators import UnicodeString

from genshi.core import Markup, stripentities

# declare your static resources here
mooeditable_js = JSLink(modname=__name__, filename='static/mooeditable/mooeditable.js', javascript=[])
mooeditable_css = CSSLink(modname=__name__, filename='static/mooeditable/mooeditable.css', javascript=[])

class MarkupConverter(UnicodeString):
    """A validator for TinyMCE widget.

    Will make sure the text that reaches python will be unicode un-xml-escaped 
    HTML content.

    Will also remove any trailing <br />s tinymce sometimes leaves at the end
    of pasted text.
    """ 
    if_missing=''
    def _to_python(self, value, state=None):
        value = super(MarkupConverter, self)._to_python(value, state)
        if value:
            value = Markup(stripentities(value)).unescape()
            return value

class EditableWidget(TextArea):
    template = "genshi:tw.mootools.templates.mooeditable"

    javascript = [moo_core_js_compressed, moo_more_js_compressed, mooeditable_js]
    css = [mooeditable_css]
    params = ['actions']
    actions = 'bold italic underline strikethrough | insertunorderedlist insertorderedlist indent outdent | undo redo | createlink unlink | urlimage | toggleview'