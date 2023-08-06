from toscawidgets.api import Widget, JSLink, CSSLink, CSSSource
from genshi.template.text import TextTemplate

from tw.mootools.base import moo_core_js_compressed, moo_js, moo_more_js

# declare your static resources here
kwick_js = JSLink(modname=__name__, filename='static/kwicks.js', javascript=[])

class KwickWidget(Widget):
    ## You can also define the template in a separate package and refer to it
    ## using Buffet style uris
    template = "genshi:tw.mootools.templates.kwick"

    javascript = [moo_core_js_compressed, kwick_js]
    
    attrs = {'height':'100px', 'backround-color':'white'}
    blockAttrs = {'height':'100px', 'width':'117px', 'backround-color':'white'}
    params = ['attrs', 'blockAttrs', 'moo_css']

    def update_params(self, d):
        self._my_update_params(d)
        Widget.update_params(self, d)
        return d

    def _my_update_params(self, d):
        values = d['value']
        d['moo_css'] = [CSSSource(self._generateCSS(values)),]
        return d
    
    cssTemplate = """${"#"}kwicks_container { 
    background-color: ${attrs.backgroundColor};
    height: ${attrs['height']};
}
${"#"}kwicks {
    position: relative;
    float: left;
    display: block;

}
 
${"#"}kwicks .kwick {
    #for a, v in attrs.iteritems()
        $a : $v ;
    #end
}
  
#for value in values
${"#"}kwick_${value.id} {
    float: left;
    display: block;
    #for a, v in value.attrs.iteritems()
         $a : $v;
    #end
    }
#end
"""
    
    def _generateCSS(self, values):
        template = TextTemplate(self.cssTemplate)
        s = template.generate(values=values, attrs=self.attrs, blockAttrs=self.blockAttrs).render()
        return s
    
