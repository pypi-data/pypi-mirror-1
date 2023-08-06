from datetime import datetime
import logging
import errno

import tw
from tw.api import CSSLink, JSLink, js_function
from tw.forms import FormField, validators

from tw.mootools.base import moo_core_js_compressed, moo_more_js_compressed

calendar_js = JSLink(modname=__name__,
                      filename='static/datepicker/DatePicker.js',
                      javascript=[])
calendar_css = CSSLink(modname=__name__,
                        filename='static/datepicker/DatePicker.css',
                        javascript=[])

class CalendarDatePicker(FormField):
    """
    Uses a javascript calendar system to allow picking of calendar dates.
    The date_format is in mm/dd/yyyy unless otherwise specified
    """
    css = [calendar_css]
    javascript = [moo_core_js_compressed, calendar_js]
    template = "tw.mootools.templates.datepicker"
    params = [
        "calendar_lang", "not_empty", "date_format"
        ]
    calendar_lang = 'en'
    not_empty = True
    date_format = "mm/dd/yyyy"
    validator = None

    _default = None

    def __init__(self, *args, **kw):
        super(CalendarDatePicker, self).__init__(*args, **kw)
        if self.default is None and self.not_empty:
            self.default = lambda: datetime.now()
        self.validator = self.validator or validators.DateTimeConverter(
            format=self.transcode_date_format(self.date_format),
            not_empty=self.not_empty
            )

    def transcode_date_format(self, value):
        return value.replace(
                            'mm','%m'
                            ).replace(
                            'dd', '%d'
                            ).replace(
                            'yyyy', '%Y'
                            ).replace(
                            'yy', '%y'
                            )
    
    def get_calendar_lang_file_link(self, lang):
        """
        Returns a CalendarLangFileLink containing a list of name
        patterns to try in turn to find the correct calendar locale
        file to use.
        """
        fname = 'static/calendar/lang/calendar-%s.js' % lang.lower()
        return JSLink(modname='tw.forms',
                      filename=fname,
                      javascript=self.javascript)

    def update_params(self, d):
        super(CalendarDatePicker, self).update_params(d)
        try:
            d.strdate = d.value.strftime(self.transcode_date_format(d.date_format))
        except AttributeError:
            d.strdate = d.value
        d.css_classes.append('DatePicker')
