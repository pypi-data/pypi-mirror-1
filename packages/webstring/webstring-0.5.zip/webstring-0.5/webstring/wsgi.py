# Copyright (c) 2006 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''WSGI middleware base class.'''

__all__ = ['WSGIBase']


class WSGIBase(object):

    '''Base class for WSGI middleware.'''
    
    def __init__(self, application, source, **kw):
        '''Initializes the class.

        @param application The WSGI application using this class must return a
        tuple or dictionary for its iterable and, at minimum, create an entry
        in the "environ" dictionary for a valid source template under the key
        "webstring.source". Other entries can be set as needed.

        Simple example:

        @template('template.html')
        def simple_app(environ, start_response):
        ... status = '200 OK'
        ... response_headers = [('Content-type','text/html')]
        ... start_response(status, response_headers)
        ... return {'test':'Hello world!\n'}        
        '''   
        self.application = application
        auto, mx = kw.get('auto', True), kw.get('max', 25)
        temps, eng = kw.get('templates'), kw.get('engine', 'etree')        
        self.encoding = kw.get('encoding', 'utf-8')
        self.format = kw.get('format', self._format)        
        self.template = self._klass(source, auto, mx, format=self._format, engine=eng, templates=temps)        

    def __call__(self, environ, start_response):
        result = self.application(environ, start_response)        
        return [str(self.template.render(result, self.format, self.encoding))]