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

'''HTML template base.'''

from xmlbase import _copytree

__all__ = ['HTMLBase']

# XML header
_xheader = u'<?xml version="1.0" encoding="%s"?>'
# XML stylesheet header
_xss = u'<?xml-stylesheet href="%s" type="text/css" ?>'
# HTML 4.01 doctype declaration
_html4 = u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
# XHTML namespace in _etree (from effbot.org/zone/element-tidylib.htm)
_xhtmlns = u'{http://www.w3.org/1999/xhtml}'
# XHTML 1.0 strict doctype declaration
_xhtml10 = u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" ' \
    '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
# XHTML 1.1 strict doctype declaration
_xhtml11 = u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" ' \
    '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'


class HTMLBase(object):
    
    '''Base class for HTML Templates.'''

    def pipe(self, info=None, format='html', encoding='utf-8'):
        '''Returns a string version of the internal element's parent and
        resets this Template.

        @param info Data to substitute into a document (default: None)
        @param format Format of document (default: 'html')
        @param encoding Encoding type for return string (default: 'utf-8')
        '''
        return super(HTMLBase, self).pipe(info, format, encoding)  
            
    def render(self, info=None, format='html', encoding='utf-8'):
        '''Returns an HTML version of the internal element's parent.

        @param info Data to substitute into a document (default: None)
        @param format HTML format to use for string (default: 'html')        
        @param encoding Encoding type for return string (default: 'utf-8')
        '''
        # Substitute any info into the document
        if info is not None: self.__imod__(info)
        tree = _copytree(self._tree)
        # Strip namespace prefix from HTML (effbot.org/zone/element-tidylib.htm)
        for elem in tree.getiterator():
            if elem.tag.startswith(_xhtmlns): elem.tag = elem.tag[len(_xhtmlns):]
        doc = self._etree.tostring(tree, encoding)
        # Output HTML 4.01
        if format == 'html':            
            # Add DOCTYPE
            doc = u'\n'.join([_html4, doc])
            # Strip namespace, empty tag closings
            doc = doc.replace(u'/>', u'>').replace(u' >', u'>')
            # Strip namespace attribute
            doc = doc.replace(u' xmlns:html="http://www.w3.org/1999/xhtml"', u'')
        # If XHTML... 
        elif format.startswith('xhtml1'):
            header, stylesheets = [_xheader % encoding], list()
            # Extract links to external styles and make them XML stylesheets
            for tag in tree.getiterator('link'):
                if tag.get('type') == 'text/css':
                    stylesheets.append(_xss % tag.get('href'))
            # Use XHTML 1.0 doctype
            if format == 'xhtml10':
                stylesheets.append(_xhtml10)
            # Use XHTML 1.1 doctype
            elif format == 'xhtml11':
                stylesheets.append(_xhtml11)
            doc = u'\n'.join([u'\n'.join(header), u'\n'.join(stylesheets), doc])
        return doc

    def write(self, path, info=None, format='html', encoding='utf-8'):
        '''Writes the string of an internal element to a file.

        @param path Path of destination file
        @param info Data to substitute into a document (default: None)
        @param format Format of document (default: 'html')
        @param encoding Encoding type for return string (default: 'utf-8')
        '''
        super(HTMLBase, self).write(path, info, format, encoding)