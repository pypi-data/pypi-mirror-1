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

'''cElementTree-based XML template engine.'''

# Python 2.5 import
try:
    from xml.etree import cElementTree as etree
# Python 2.4 import
except ImportError:
    import cElementTree as etree
# Try importing elementtidy for broken HTML handling w/ cElementTree
try:
    from elementtidy import TidyHTMLTreeBuilder as tidy
except ImportError: pass
from webstring.xmlbase import *
from webstring.htmlbase import HTMLBase

__all__ = ['EtreeTemplate', 'EtreeHTML']

# elementtidy error message
msg = 'Broken HTML requires elementtidy from http://effbot.org/downloads/'

def _copyhtml(tree):
    '''Copies an HTML document while striping the tidy meta tag.'''
    newdoc = _copytree(tree)
    # Strip HTML Tidy meta tag
    for parent in newdoc.getiterator():
        for child in parent:
            if child.tag.endswith('meta'):
                if child.get('content').startswith('HTML Tidy'):
                    parent.remove(child)
    return newdoc


class _EtreeField(_XMLField):

    '''cElementTree Field class.'''
    
    _etree, _group, _klass = etree, None, _XMLOne


class _EtreeGroup(object):

    '''cElementTree Group class.'''    

    def __new__(cls, *args, **kw):
        c = _XMLGroup
        c._etree, c._group, c._field = etree, _XMLGroup, _EtreeField 
        return c(*args, **kw) 


_EtreeField._group = _EtreeGroup    
  

class EtreeTemplate(_XMLTemplate):

    '''cElementTree-based root Template class.'''
    
    _etree, _field, _group = etree, _EtreeField, _EtreeGroup       
             
    # Create property that returns the current Template state   
    current = property(lambda self: EtreeTemplate(_copytree(self._tree),
        self._auto, self._max, templates=self._templates))
    # Create property that returns the default Template state
    default = property(lambda self: EtreeTemplate(_copytree(self._btree),
        self._auto, self._max, templates=self._templates))


class EtreeHTML(HTMLBase, EtreeTemplate):

    '''ElementTree HTML Template class.'''    

    def fromfile(self, path):
        '''Creates an internal element from a file source.

        @param path Path to a template source
        '''
        # Try ordinary XML parsing
        try:
            super(EtreeHTML, self).fromfile(path)
        # Try feeding through tidy
        except:            
            # Try elementtidy to handle broken HTML
            try:
                self._setelement(_copyhtml((tidy.parse(path).getroot())))
            # Raise error if no elementtidy
            except NameError:
                raise ImportError(msg)
            
    def fromstring(self, instring):
        '''Creates an internal element from a string source.

        @param path String source for an internal template
        '''
        # Try parsing the string as plain old XML
        try:
            super(EtreeHTML, self).fromstring(instring)
        # Try feeding it through tidy
        except:
            # Try elementtidy to handle broken HTML
            try:
                parser = tidy.TreeBuilder()
                parser.feed(instring)
                self._setelement(_copyhtml(parser.close()))
            # Raise error if no elementtidy
            except NameError:
                raise ImportError(msg)   