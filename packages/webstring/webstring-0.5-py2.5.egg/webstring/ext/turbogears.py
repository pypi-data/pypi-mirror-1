# Copyright (c) 2005, the Lawrence Journal-World
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
#    3. Neither the name of Django nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
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

'''webstring plugin for TurboGears and Buffet'''

from webstring import Template

def _get_mod_func(callback):
    '''Breaks a callable name out from a module name.

    @param callback Name of a callback        
    '''
    dot = callback.rindex('.')
    return callback[:dot], callback[dot+1:]

def _get_callback(callback):
    '''Loads a callable based on its name

    callback A callback's name'''        
    mod_name, func_name = _get_mod_func(callback)
    try:
        return getattr(__import__(mod_name, '', '', ['']), func_name)
    except ImportError, error:
        raise ImportError(
            'Could not import %s. Error was: %s' % (mod_name, str(error)))
    except AttributeError, error:
        raise AttributeError(
            'Tried %s in module %s. Error was: %s' % (func_name,
             mod_name, str(error)))


class TurboWebstring(object):

    '''webstring support for TurboGears and Buffet.'''    

    def __init__(self, extra_vars_func=None, options=None):
        '''
        @param extra_vars_func Not used
        @param options Extra settings for webstring Template
        '''
        if options is None: options = dict()
        self.options = options
        # Sets XML template engine
        self.engine = options.get('webstring.engine', 'etree')
        # Sets text encoding
        self.encoding = options.get('webstring.encoding', 'utf-8')
        # Sets any templates
        self.templates = options.get('webstring.templates')
        # Sets document format of output
        self.format = options.get('webstring.format', 'html')
        # Turns off mapping fields to object attributes
        self.auto = options.get('webstring.auto', False)
        # Sets maximum repetition
        self.max = options.get('webstring.max', 25)
        # Sets template file
        self.template = options.get('webstring.template')
        # Create template object if passed a template file source
        if self.template is not None:
            self.template = Template(self.template, self.auto, self.max,
                templates=self.templates, engine=self.engine, format=self.format)
        else:
            self.callable = options.get('webstring.callable')


    def load_template(self, classname):
        '''Loads a callable function that accepts a single argument for info.
    
        @param classname The name of the function
        @param loadingSite Not used
        '''
        self.callable = _get_callback(classname)

    def render(self, info, format='html', fragment=False, template=None):
        '''Renders data in the desired format.
    
        @param info The data
        @param format Format to render data to (default: 'html') 
        @param fragment Not used
        @param template Name of a template (default: None)
        '''
        # Create new template object arg passed to render
        if template is not None:
            template = Template(template, self.auto, self.max,
                templates=self.templates, engine=self.engine,
                format=self.format)
        # Otherwise, use any template object created on initialization 
        else:
            template = self.template
        # If callable set, pass info to callable
        if self.callable is not None: return self.callable(info)
        # Return output
        return template.render(info, format, self.encoding)

    def transform(self, info, template):
        '''Stub for compatibility.'''
        pass