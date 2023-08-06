"""Display Subversion URLs in the Browse Source section."""

import re

from trac.core import *
from trac.config import Option
from trac.web import IRequestFilter
from trac.web.chrome import add_ctxtnav

class BrowserLinkAdder(Component):
    implements(IRequestFilter)

    svn_base_url = Option('svn', 'repository_url',
                          doc="base URL of svn repository")
    pattern = re.compile(r'/browser(/.*|$)')

    def url(self, path):
        return u'/'.join((self.svn_base_url.rstrip(u'/'), path.lstrip(u'/')))

    ### IRequestFilter methods
    
    def pre_process_request(self, req, handler):
        """Stick the Subversion Location link in the contextual nav when applicable."""
        match = self.pattern.match(req.path_info)
        if match:  # TODO: perhaps test handler instead
            add_ctxtnav(req, 'Subversion Location', href=self.url(match.group(1)), title="This location in the Subversion repository")
        return handler
    
    def post_process_request(self, req, template, data, content_type):
        """Do nothing."""
        return template, data, content_type
