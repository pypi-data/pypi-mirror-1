# Created by Noah Kantrowitz on 2007-08-28.
# Copyright (c) 2007 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.web.api import IRequestFilter
from trac.web.chrome import INavigationContributor
from trac.util.html import html as tag

class NavPlusModule(Component):
    """The filter to add/remove/migrate navigation items."""

    implements(INavigationContributor)
    
    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler
            
    def post_process_request(self, req, template, content_type):
        
        
        return template, content_type
        
    # INavigationContributor methods
    def get_active_navigation_item(self, req):
        return ''

    def get_navigation_items(self, req):
        for key, value in self.config.options('navplus'):
            if value == 'mainnav' or value == 'metanav':
                title = self.config.get('navplus', key+'.title') or ''
                url = self.config.get('navplus', key+'.url') or ''
                if not url.startswith('/') and ':' not in url:
                    url = req.href(url)
                yield value, key, tag.a(title, href=url)


