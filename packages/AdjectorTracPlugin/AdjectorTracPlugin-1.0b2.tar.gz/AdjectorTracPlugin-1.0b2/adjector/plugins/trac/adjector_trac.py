#-------------------------------------------------------------------------
# Copyright 2009-2010 David Isaacson, Stou Sandalski, Information Capsid
#
# This file is part of the program Adjector.
#
# Adjector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) version 3 of the License.
#
# Adjector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adjector. If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------

from adjector.client import initialize_adjector, render_zone
from trac.core import Component, implements
from trac.web.api import IRequestFilter

class AdjectorTracPlugin(Component):
    implements(IRequestFilter)

    #magic self variables: env, config, log
    
    def __init__(self):
        self.log.error('ADJECTOR')
        config = dict(self.config.options('adjector'))
        initialize_adjector(config)
            
    #IRequestFilter
    """Extension point interface for components that want to filter HTTP
    requests, before and/or after they are processed by the main handler."""
    
    def pre_process_request(self, req, handler):
        """Called after initial handler selection, and can be used to change
        the selected handler or redirect request.
       
        Always returns the request handler, even if unchanged.
        """
        return handler

    # for ClearSilver templates
    def post_process_request(self, req, template, content_type):
        """Do any post-processing the request might need; typically adding
        values to req.hdf, or changing template or mime type.
       
        Always returns a tuple of (template, content_type), even if
        unchanged.

        Note that `template`, `content_type` will be `None` if:
         - called when processing an error page
         - the default request handler did not return any result

        (for 0.10 compatibility; only used together with ClearSilver templates)
        """
        return (template, content_type)

    # for Genshi templates
    def post_process_request(self, req, template, data, content_type):
        """Do any post-processing the request might need; typically adding
        values to the template `data` dictionary, or changing template or
        mime type.
       
        `data` may be update in place.

        Always returns a tuple of (template, data, content_type), even if
        unchanged.

        Note that `template`, `data`, `content_type` will be `None` if:
         - called when processing an error page
         - the default request handler did not return any result

        (Since 0.11)
        """
        
        data['render_zone'] = render_zone
        
        return (template, data, content_type)