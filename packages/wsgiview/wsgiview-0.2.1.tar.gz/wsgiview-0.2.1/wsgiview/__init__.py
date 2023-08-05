# Copyright (c) 2006 L. C. Rees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of wsgiview nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Use TurboGears Template Plug-ins Anywhere.'''

__author__ = 'L. C. Rees <lcrees-at-gmail.com>'
__revision__ = '0.2'

import pkg_resources

__all__ = ['WsgiView', 'view']

# Load available TurboGears/Buffet plug-ins
_engines = dict((_engine.name, _engine) for _engine in
    pkg_resources.iter_entry_points('python.templating.engines'))

def view(template=None, **kw):
    '''Decorator for WsgiView.

    @param template A template name
    '''
    def decorator(application):
        return WsgiView(application, template, **kw)
    return decorator


class WsgiView(object):

    '''TurboGears/Buffet Template Plug-in WSGI Middleware.'''

    engine = None    

    def __init__(self, application, template=None, **kw):
        if template is not None:
            # Template is passed in form 'templateName:templatePath'
            # 'templateName' is the prefix of the template engine e.g. 'kid'
            # 'templatePath' is a location minus extension in the PYTHONPATH            
            engine_name, template = template.split(':')
            # Get parameters
            extra_vars_func = kw.get('extra_vars')
            options = kw.get('options', dict())
            # Load and instantiate engine
            engine = _engines[engine_name].load()
            self.engine = engine(extra_vars_func, options)
        self.format = kw.get('format', 'html')
        self.fragment = kw.get('fragment', False)
        self.application, self.template = application, template

    def __call__(self, environ, start_response):
        # Get info dict from WSGI app
        info = self.application(environ, start_response)
        # See if app specified its own engine
        engine_name = environ.get('wsgiview.engine')
        # Load new engine if app calls for it
        if engine_name is not None:
            extra_vars_func = environ.get('wsgiview.extra_vars_func')
            options = environ.get('wsgiview.options')
            engine = _engines[engine_name].load()
            engine = engine(extra_vars_func, options)
        # By default, use template passed to class constructor
        else:
            engine = self.engine
        # Get app-specified template using self.template as default
        template = environ.get('wsgiview.template', self.template)
        # Get app-specified format using self.format as default
        format = environ.get('wsgiview.format', self.format)        
        fragment = environ.get('wsgiview.fragment', self.fragment)
        # Call plug-in's render method to return a string
        return [str(engine.render(info, format, fragment, template))]    