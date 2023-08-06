import os
import tw
from tw.api import Widget, JSLink, CSSLink, Link
from tw.core.resources import registry, working_set, Requirement
from defaults import __TIMELINE_VERSION__

class TimelineLinkMixin(Link):
    params = {'version': '(string) select the yui version you would like to use. Default version is: '+__TIMELINE_VERSION__,
    }

    extension = 'js'
    version = __TIMELINE_VERSION__

    def __init__(self, *args, **kw):
        super(Link, self).__init__(*args, **kw)
        modname = self.modname or self.__module__
        self.webdir, self.dirname, self.link = registry.register(
            modname, self.filename
            )

    
    def _get_link(self):
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
        basename = self.basename.replace('/', os.sep)
        basename = self.basename.replace('\\', os.sep)

        basename = os.sep.join(('static', self.version, 'api', basename))
        #try the default
        filename =  basename+'.'+self.extension
        if self.try_filename(filename):
            return filename
        
        raise NotImplementedError('could not find a javascript file in the library with that name')
    


class TimelineJSLink(JSLink, TimelineLinkMixin):
    pass

class TimelineCSSLink(TimelineLinkMixin, CSSLink):
    extension = 'css'
