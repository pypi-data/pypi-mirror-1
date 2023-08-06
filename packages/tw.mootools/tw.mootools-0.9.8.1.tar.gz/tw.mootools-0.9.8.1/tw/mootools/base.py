from tw.api import Widget, JSLink, CSSLink, Link
from tw.core.resources import registry, working_set, Requirement
from tw.mootools.defaults import __MOOTOOLS_VERSION__, __DEFAULT_MODULE__, __DEFAULT_SUFFIX__

import tw

import os

#__all__ = ["Twtools"]

class DomElementWithValue(object):
    def __init__(self, id, value, attrs={}):
        self.id = id
        self.attrs = attrs
        self.value = value

class MootoolsLink(Link):
    params = {'basename': '(string) basename for the given file.  if you want mootools-core.js, the base is mootools',
              'suffix': '(string) yc (yui compressed), jm (jsmin compressed) or nc (not compressed).  Default is "yc"',
              'part': '(string) core or more.  Default is "core"',
              'version': '(string) select the mootools version you would like to use. Default version is: '+__MOOTOOLS_VERSION__,
    }

    version = __MOOTOOLS_VERSION__
    modname = "tw.mootools"
    extension = 'js'
    part = __DEFAULT_MODULE__
    suffix = __DEFAULT_SUFFIX__

    def __init__(self, *args, **kw):
        super(Link, self).__init__(*args, **kw)
        if not self.is_external:
            modname = self.modname or self.__module__
            self.webdir, self.dirname, self.link = registry.register(
                self, modname, self.filename
                )
            
        if 'suffix' in kw:
            self.suffix = kw['suffix']
            
        if 'part' in kw:
            self.part = kw['part']

    def _get_link(self):
        if self.is_external:
            return self.external_link
        return tw.framework.url(self._link or '')

    def _set_link(self, link):
        self._link = link

    link = property(_get_link, _set_link)

    def abspath(self, filename):
        return os.sep.join((os.path.dirname(__file__), filename))

    def try_filename(self, filename):
        abspath = self.abspath(filename)
        if os.path.exists(abspath):
            return filename
        return False

    @property
    def filename(self):
        #make basename windows/qnix compat
        basename = os.sep.join(('static', self.version, 'mootools'))
        #try the default
        filename =  basename+'-'+self.version+'-'+self.part+'-'+self.suffix+'.'+self.extension
        return filename

class MootoolsCoreLink(JSLink, MootoolsLink):
    pass
class MootoolsMoreLink(JSLink, MootoolsLink):
    part = 'more'
    
## JS dependencies can be listed at 'javascript' so they'll get included
## before
moo_core_js    = MootoolsCoreLink(suffix='nc')
moo_core_js_compressed    = MootoolsCoreLink(suffix='yc')

moo_more_js    = MootoolsMoreLink(suffix='nc')
moo_more_js_compressed    = MootoolsMoreLink(suffix='yc')

# for backward compat
moo_js = moo_core_js
moo_js_compressed = moo_core_js_compressed

    
class MooTools(Widget):
    template = """<span xmlns:py="http://genshi.edgewall.org/" py:strip="true"></span>"""
    
    def __init__(self, version=None):
        self.version = version
    
    @property
    def javascript(self):
        if self.version:
            return [
                  MootoolsCoreLink(version=self.version),
                  MootoolsMoreLink(version=self.version),
                 ]
        else:
            return [
                  MootoolsCoreLink(),
                  MootoolsMoreLink(),
                 ]

# for backward compat
MooToolsCompressed = MooTools