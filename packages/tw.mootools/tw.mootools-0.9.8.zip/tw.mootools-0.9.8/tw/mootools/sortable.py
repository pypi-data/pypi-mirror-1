from tw.api import Widget, JSLink, CSSLink, CSSSource, JSSource
from genshi.template.text import TextTemplate
from base import DomElementWithValue, moo_core_compressed_js

# declare your static resources here
widget_js = JSLink(modname=__name__, filename='static/sortable.js', javascript=[])

class SortableWidget(Widget):
    ## You can also define the template in a separate package and refer to it
    ## using Buffet style uris
    template = "genshi:tw.mootools.templates.sortable"

    javascript = [moo_core_js]

    #attributes for the entire widget
    attrs = {'width':'300px', 'backround-color':'white'}

    #attributes that are the same across blocks
    blockAttrs = {}
    
    params = ['attrs', 'blockAttrs', 'widget_css', 'widget_js', 'onComplete']

    onComplete = "console.log('got to onComplete')"
    
    def update_params(self, d):
        self._my_update_params(d)
        Widget.update_params(self, d)
        return d

    def _my_update_params(self, d):
        values = d['value']
        d['widget_css'] = [CSSSource(self._generateCSS(values)),]
        return d
    
    cssTemplate = """${"#"}${id} { 
	position: inherit;
}
 
ul${"#"}sortables {
	width: 300px;
	margin: 0;
	padding: 0;
#for a, v in attrs.iteritems()
    ${a} : ${v};
#end
}
 
#for value in values
    li.sortable_${value.id} {
            padding: 4px 8px;
            cursor: pointer;
            list-style: none;
    #for a, v in value.attrs.iteritems()
            ${a} : ${v};
    #end
    }
#end
 
ul${"#"}sortables li {
	margin: 10px 0;
}


"""
    
    def _generateCSS(self, values):
        template = TextTemplate(self.cssTemplate)
        s = template.generate(values=values, blockAttrs=self.blockAttrs, attrs=self.attrs, id=self.id).render()
        return s
    
