import tw.forms
import tw.api
from tw.api import Widget, JSLink, CSSLink, CSSSource

from tw.forms import InputField, InputWidget, CalendarDatePicker

from tw.mootools.base import moo_core_js_compressed, moo_more_js_compressed

formcheck_js = JSLink(modname=__name__,
                      filename='static/formcheck/formcheck.js',
                      javascript=[])
formcheck_css = CSSLink(modname=__name__,
                        filename='static/formcheck/theme/classic/formcheck.css',
                        javascript=[])

twmootoolsforms_js = JSLink(modname=__name__,
                      filename='static/forms.js',
                      javascript=[])

def set_widgets_validator_classes(widget):
    validator_name = widget.validator.__class__.__name__
    if validator_name == 'All':
        validator_names = widget.validator.validators
    else:
        validator_names = [validator_name]
        
    for validator in validator_names:
        validator_name = widget.validator.__class__.__name__
        if validator_name == 'MinLength':
            validator_name += " validate['length[%d,-1]']" % validator.minLength
            
        if validator_name == 'NotEmpty' or (hasattr(widget, 'is_required') and widget.is_required):
            validator_name += " validate['required']"
            
        if validator_name == 'Int':
            validator_name += " validate['digit']"
            
        widget.css_classes.append(validator_name)
        
    if widget.attrs.get('class'):
        widget.attrs['class'] += ' ' + validator_name
    if hasattr(widget, 'children'):
        for child in widget.children:
            set_widgets_validator_classes(child)

class CustomisedForm(tw.forms.Form):
    """A form that allows specification of several useful client-side behaviours.
    Inherits all features of tw.dynforms.CustomisedForms plus client side validation"""
    params = {
        'blank_deleted': 'Blank out any deleted form fields from GrowingTable on the page. This is required for growing to function correctly - you must use GrowingTableFieldSet within a CustomisedForm with this option set.',
        # TBD: 'save_prompt': 'If the user navigates away without submitted the form, and there are changes, this will prompt the user.',
        'disable_enter': 'Disable the enter button (except with textarea fields). This reduces the chance of users accidentally submitting the form.',
        'validate_inputs': 'When the user clicks the submit button, verify that all required fields are entered'
    }
    blank_deleted = True
    #save_prompt = True
    disable_enter = True
    validate_inputs = True
    javascript = [moo_core_js_compressed,
                  moo_more_js_compressed,
                  formcheck_js,
                  twmootoolsforms_js]
    css = [formcheck_css]
    form_lang = 'en'
    
    
    def __init__(self, *args, **kwargs):
        super(CustomisedForm, self).__init__(*args, **kwargs)
        #set_widgets_validator_classes(self)
        
    def get_form_lang_file_link(self, lang):
        """
        Returns a CalendarLangFileLink containing a list of name
        patterns to try in turn to find the correct calendar locale
        file to use.
        """
        fname = 'static/formcheck/lang/%s.js' % lang
        return JSLink(modname=__name__,
                      filename=fname,
                      javascript=self.javascript)
    
    
    def update_params(self, params):
        super(CustomisedForm, self).update_params(params)
        if params.get('validate_inputs', self.blank_deleted):
            params.css_classes.append('validate_form')
            
        if params.get('blank_deleted', self.blank_deleted):
            params.setdefault('attrs', {})['onsubmit'] = 'twd_blank_deleted()'
        if params.get('disable_enter', self.disable_enter):
            self.add_call('document.onkeypress = twd_suppress_enter;')
        
        set_widgets_validator_classes(self)
        
        self.get_form_lang_file_link(self.form_lang).inject()