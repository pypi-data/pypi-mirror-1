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

'''XML Template engine.'''

from webstring.etreet import EtreeTemplate
from webstring.lxmlt import LxmlTemplate
from webstring.wsgi import WSGIBase

__all__ = ['XMLTemplate', 'WSGITemplate', 'template']

def template(source, **kw):
    '''Decorator for general templating.'''
    def decorator(application):
        return WSGITemplate(application, source, **kw)
    return decorator


class XMLTemplate(object):

    '''XML template class.'''
    
    def __new__(cls, *args, **kw):
        engine = kw.get('engine', 'etree')
        if engine == 'lxml':
            return LxmlTemplate(*args, **kw)
        elif engine == 'etree':
            return EtreeTemplate(*args, **kw)


class WSGITemplate(WSGIBase):

    '''WSGI middleware for using XMLTemplate to render web content.'''

    _format, _klass = 'xml', XMLTemplate        