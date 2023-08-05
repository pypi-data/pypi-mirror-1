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

'''Base webstring Template classes.'''

import string
from keyword import kwlist

__all__ = ['_Template', '_Group', '_Field', '_checkname']

# Exceptions
_exceptions = ['maximum allowed repetitions exceeded',
    'invalid Template source',
    'invalid type for formatting',
    'not all arguments converted during formatting',
    'not enough arguments for format', '', '',
    'invalid inline template source',
    'delimiter "$" or "%" not found',
    'invalid Template filter type']
_Stemplate = string.Template
# Illegal characters for Python names
_ichar = '()[]{}@,:.`=;+-*/%&|^><\'"#\\$?!~'
# Reserve webstring specific words
kwlist.extend(['append', 'atemplates', 'current', 'default', 'exclude',
    'fromfile', 'fromstring', 'groupmark', 'include', 'mark', 'max', 'pipe',
    'purge', 'render', 'repeat', 'reset', 'template', 'templates', 'text',
    'update', 'write'])
_reserve, _keywords = string.maketrans('', ''), frozenset(kwlist)

def _checkname(name):
    '''Ensures a string is a legal Python name.'''
    # Remove characters that are illegal in a Python name
    if '}' not in name:
        name = name.replace('.', '_').translate(_reserve, _ichar)
    # Handle XML namespaced names
    else:
        name = name.split('}')[1].replace('.', '_').translate(_reserve, _ichar)
    # Add _ if value is a Python keyword
    if name in _keywords: return ''.join([name, '_'])
    return name
    

class _Base(object):

    '''Template base class.'''

    def __init__(self, auto, **kw):
        # Controls if templates become object attrs of a root/group Template
        self._auto = auto

    def __repr__(self):
        '''String representation of a Template.'''
        return '<Template "%s" at %x>' % (self.__name__, id(self))

    def __str__(self):
        '''String output of a Template.'''
        return self.render()

    def __add__(self, data):
        '''Inserts data or another Template's fields after the internal
        template and returns a modified copy of the Template.
        '''
        self.__iadd__(data)
        newself = self.current
        self.reset()
        return newself

    def __radd__(self, data):
        '''__add__ from the right.'''
        return self.__add__(data)
   
    def __mul__(self, num):
        '''Inserts a copy of the internal field after the internal field 
        "num" number of times and returns a modified copy of the Template.
        '''
        self.__imul__(num)
        newself = self.current
        self.reset()
        return newself

    def __rmul__(self, num):
        '''__mul__ from the right.'''
        return self.__mul__(num)
        
    def __imul__(self, num):
        '''Inserts a copy of the internal field after the internal field 
        "num" number of times and the Template (self) is returned modified.
        '''
        # Ensure "num" is not greater than maximum allowed repetitions
        if num <= self.max:            
            tmp = self.current
            # Concatenate "number" number of copies of self to self
            for number in xrange(num-1): self.__iadd__(tmp.current)
            return self
        raise TypeError(_exceptions[0])

    def __mod__(self, data):
        '''Substitutes text data into the internal template and returns a
        modified copy of the Template.
        '''
        self.__imod__(data)
        newself = self.current
        self.reset()
        return newself
               
    def __pow__(self, data):
        '''For each item in a tuple, the internal template is copied, the
        item is substituted into the copy's template, and the copy is inserted
        after the internal template. Finally, a modified copy of the Template
        is returned.
        '''
        self.__ipow__(data)
        newself = self.current
        self.reset()
        return newself

    def __ipow__(self, data):
        '''For each item in a tuple, the internal template is copied, the 
        content of the item is substituted into the copy's template, and
        the copy is inserted after the internal template. Finally, the modified
        Template (self) is returned.
        '''
        if len(data) <= self.max:
            if isinstance(data, tuple):
                # Put data in correct order
                data = list(reversed(data))
            else:
                raise TypeError('invalid type for formatting')
            # Substitute content into existing field
            self.__imod__(data.pop())
            # Concatenate a new field with self for each item
            while data: self.repeat(data.pop())
            return self                
        # Raise exception if data length > maximum allowed repetitions
        raise TypeError(_exceptions[0])

    def _setmark(self, mark):
        '''Sets template variable delimiter.'''
        self._mark = mark

    def pipe(self, info=None, format='xml', encoding='utf-8'):
        '''Returns the string output of the internal template and
        resets the Template.

        @param info Data to substitute into a template (default: None)
        @param format Document format (default:'xml')
        @param encoding Encoding of return string (default: 'utf-8')
        '''
        output = self.render(info, format, encoding)
        self.reset()
        return output

    def repeat(self, data=None):
        '''Copies the original state of the internal template, inserts it after
        the interal template, and, optionally, substitutes data into it.

        @data data Data to substitute into a template (default: None)
        '''
        if data is not None:
            self.__iadd__(self.default.__imod__(data))
        else:
            self.__iadd__(self.default)
            
    def write(self, path, info=None, format='xml', encoding='utf-8'):
        '''Writes a Template's string output to a file.

        @param path Output file path
        @param info Data to substitute into a template (default: None)
        @param format Document format (default:'xml')
        @param encoding Encoding of output string (default: 'utf-8')
        '''
        open(path, 'wb').write(self.render(info, format, encoding))


class _Many(_Base):

    '''Base class for Templates with subtemplates (groups or fields).'''

    def __init__(self, auto, omax, **kw):
        super(_Many, self).__init__(auto, **kw)
        # Sets maximum allowed repetitions of a Template
        self._max = omax
        # Internal tracking structures
        self._fielddict, self._fields, self._filter = dict(), list(), set()

    def __imod__(self, data):
        '''Substitutes text data into each field's template and the
        modified Template (self) is returned.
        '''
        # Get any templates
        try:
            self.templates(data.pop('templates'))
        except (AttributeError, KeyError): pass
        # Get any substitutions
        try:
            self.__ipow__(data.pop('subs'))
        except (AttributeError, KeyError): pass
        # Cache field and data length
        lself, length = len(self._fields), len(data)
        # If number of fields == number of items in data...
        if length == lself:
            if isinstance(data, dict):                
                for key, value in data.iteritems():
                    # If tuple, expand it
                    try:
                        self._fielddict[key].__ipow__(value)
                    # If dictionary, substitute it
                    except TypeError:
                        self._fielddict[key].__imod__(value) 
            elif isinstance(data, tuple):
                # Iterate with index and item through data
                for key, item in enumerate(data):
                    # If item is a tuple, expand it
                    try:
                        self._fields[key].__ipow__(item)
                    # If dictionary, substitute it
                    except TypeError:
                        self._fields[key].__imod__(item)
            else:
                raise TypeError(_exceptions[2])
        # Return self if no more items in data
        elif length == 0:
            return self
        # Raise exception if too many items to match all fields
        elif length > lself:
            raise TypeError(_exceptions[3])
        # Raise exception if too few items to match all fields
        elif length < lself:
            raise TypeError(_exceptions[4])        
        return self 

    def __getitem__(self, key):
        '''Gets a field by position or keyword.'''
        # Try getting field by position from list
        try:
            return self._fields[key]
        # Try getting field by keyword from dictionary
        except TypeError:
            return self._fielddict[key]
    
    def __setitem__(self, key, value):
        '''Stub'''
        
    def __delitem__(self, key):
        '''Deletes a field.'''
        # Handle positional indexes
        try:
            # Get field
            obj = self._fields[key] 
            # Get field name
            for name, element in self._fielddict.iteritems():
                if element == obj: break
        # Handle keys
        except TypeError:
            name = key
        # Delete object attribute
        self.__delattr__(name)

    def __contains__(self, key):
        '''Tells if a field of a given name is in a Template.'''
        return key in self._fielddict        

    def __len__(self):
        '''Gets the number of fields in a Template.'''
        return len(self._fields)    

    def __iter__(self):
        '''Iterator for the internal field list.'''
        return iter(self._fields)

    def _setfield(self, key, node):
        '''Sets a new field.'''
        self._fields.append(node)        
        self._fielddict[key] = node
        # Make field attribute of self if automagic on
        if self._auto: setattr(self, key, node)

    def _setmark(self, mark):
        '''Sets the variable delimiter for all subtemplates in a Template.'''
        super(_Many, self)._setmark(mark)
        # Set variable delimiter on all children
        for field in self._fields: field.mark = mark          

    def _setgmark(self, mark):
        '''Sets group delimiter.'''
        self._groupmark = mark

    def _setmax(self, omax):
        '''Sets the maximum repetition value for all Templates.'''
        # Set group or root to max
        self._max = omax
        # Set max on all children
        for field in self._fields: field.max = omax            
    
    # Property for setting a maximum repetition value    
    max = property(lambda self: self._max, _setmax)    
    

class _Field(_Base):

    '''Field base class.'''
    
    def __init__(self, auto, omax, **kw):
        super(_Field, self).__init__(auto, **kw)
        # Maximum repetition value and internal trackers
        self.max, self._siblings = omax, kw.get('siblings', list())
        self._tempfields = kw.get('tempfields', list())

    def __imod__(self, data):
        '''Substitutes text data into the internal element's text and
        attributes and returns this field (self) modified.
        '''
        if isinstance(data, basestring):
            self.text = data
        elif isinstance(data, dict):            
            # Try popping inline text content
            try:
                self.text = data.pop('text')
            except KeyError: pass
            # Try popping substitutions
            try:
                self.__ipow__(data.pop('sub'))                
            except KeyError: pass
        else:
            raise TypeError(_exceptions[2])
        return self
        

class _Group(_Many):

    '''Group base class.'''    

    def __init__(self, auto, omax, **kw):
        super(_Group, self).__init__(auto, omax, **kw)
        # Internal trackers
        self._siblings = kw.get('siblings', list())
        self._tempfields = kw.get('tempfields', list())


class _Template(_Many):

    '''Base class for root Templates.'''    

    def __init__(self, auto, omax, **kw):
        super(_Template, self).__init__(auto, omax, **kw)      

    def append(self, data):        
        '''Makes a string or another Template's internal template part of
        the Template's internal template.

        @param data Template or element
        '''
        self.__iadd__(data)   

    def exclude(self, *args):
        '''Excludes fields or groups from a Template.

        @param args Names of a field or group
        '''
        # Remove fields from root
        for arg in args:
            name = _checkname(arg)
            # Add to internal filter list
            self._filter.add(name)
            # Remove field if present
            self.__delitem__(name)
        # Remove fields from children
        for index, field in enumerate(self._fields):
            # Run only on groups
            if hasattr(field, 'groupmark'):
                for arg in args:                    
                    name = _checkname(arg)
                    # Remove subfield if present
                    field.__delitem__(name)                    
                # Remove empty groups
                if len(field) == 0: self.__delitem__(index)    

    def include(self, *args):
        '''Includes a field or group in a Template.

        @param args Names of fields or groups
        '''
        # Remove from internal tracker
        self._filter -= set(args)
        self.reset()