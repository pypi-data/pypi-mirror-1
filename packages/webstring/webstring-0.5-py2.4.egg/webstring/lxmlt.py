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

'''lxml-based XML template engine.'''

try:
    import lxml.etree as etree  
except ImportError:
    raise ImportError('LxmlTemplate needs the lxml library')
from webstring.xmlbase import *
from webstring.htmlbase import HTMLBase

__all__ = ['LxmlTemplate']


class _LxmlBase(object):

    '''lxml specific methods.'''    

    _xslt = None    

    def _setxslt(self, stylesheet):
        '''Sets the XSLT stylesheet for a template.'''
        self._xslt = self._etree.XSLT(self._etree.XML(stylesheet))

    def transform(self, stylesheet=None, **kw):
        '''Transforms a template based on an XSLT stylesheet.

        @param stylesheet XSLT document (default: None)
        @param kw Keyword arguments
        '''
        if stylesheet is not None: self._setxslt(stylesheet)
        return str(self._xslt(self._tree, **kw))

    def xinclude(self):
        '''Processes any xinclude statements in the internal template.'''
        eobj = self._etree.ElementTree(self._tree)
        eobj.xinclude()        

    # XSLT property
    xslt = property(lambda self: self._xslt, _setxslt)    


class _LxmlOne(_XMLOne, _LxmlBase):

    '''lxml-based Field base class.'''    

    _etree = etree

    def __init__(self, *arg, **kw):
        super(_LxmlOne, self).__init__(*arg, **kw)


class _LxmlField(_XMLField):

    '''lxml-based Field dispatcher.'''

    _etree, _group, _klass = etree, None, _LxmlOne


class _LxmlGroup(object):

    '''lxml-based Group class.'''    

    def __new__(cls, *args, **kw):
        _XMLGroup._etree, _XMLGroup._field, _XMLGroup._group = etree, _LxmlField, cls
        return type('_LxmlGroup', (_XMLGroup, _LxmlBase), {})(*args, **kw)


_LxmlField._group = _LxmlGroup


class LxmlTemplate(_XMLTemplate, _LxmlBase):

    '''lxml-based root Template class.'''

    _etree, _field, _group = etree, _LxmlField, _LxmlGroup    

    # Create property that returns the current Template state   
    current = property(lambda self: LxmlTemplate(_copytree(self._tree),
        self._auto, self._max, templates=self._templates))
    # Create property that returns the default Template state
    default = property(lambda self: LxmlTemplate(_copytree(self._btree),
        self._auto, self._max, templates=self._templates)) 


class LxmlHTML(HTMLBase, LxmlTemplate):
    
    '''Template class for HTML documents.'''
    
    def fromfile(self, path):
        '''Creates an internal element from a file source.

        @param path Path to a template source
        '''
        # Try ordinary XML parsing
        try:
            super(LxmlHTML, self).fromfile(path)
        # Feed through the HTML parser to handle broken HTML
        except:
            parser = self._etree.HTMLParser()
            self._setelement(self._etree.parse(path), parser)
            
    def fromstring(self, instring):
        '''Creates an internal element from a string source.

        @param path String source for an internal template
        '''
        # Try parsing the string as straight XML
        try:
            super(LxmlHTML, self).fromstring(instring)
        # Feed through the HTML parser to handle broken HTML
        except:
            self._setelement(self._etree.HTML(instring))    