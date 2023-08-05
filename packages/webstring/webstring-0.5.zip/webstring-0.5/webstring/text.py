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

'''Text template base classes.'''

import re
from copy import deepcopy
from webstring.base import _Template, _Field, _Group, _exceptions, _checkname
from webstring.wsgi import WSGIBase 

__all__ = ['TextTemplate', 'WSGITextTemplate', 'texttemplate']

# Default variable and group delimiter
MARK = GROUPMARK = '$'
# Variable and group discovery regex
PATTERN = r'%s{2}(.+?)%s{2}|%s{1}(\w+?)%s{1}'

def getpattern(mark=MARK, group=GROUPMARK):
    '''Fetches a regex pattern set with the current delimiters for a Template.

    @param mark Variable delimiter (default: MARK)
    @param group Group delimiter (default: GROUPMARK)
    '''
    # Escape delimiters
    mark, group = re.escape(mark), re.escape(group)
    # Arrange in tuple
    marks = (group, group, mark, mark)
    # Return compiled regex pattern
    return re.compile(PATTERN % marks, re.DOTALL|re.UNICODE)

# Default regex pattern
_match = getpattern()

def texttemplate(source, **kw):
    '''Decorator for text templating.'''
    def decorator(application):
        return WSGITextTemplate(application, source, **kw)
    return decorator


class _NonRoot(object):

    '''Base class for non-root text Templates.'''

    def append(self, data):        
        '''Appends a string or another Template's template to the
        Template's internal template.

        @param data Template or string
        '''
        return self.__iadd__(data)

    # Create property that returns the current state   
    current = property(lambda self: deepcopy(self))


class _TextField(_Field, _NonRoot):

    '''Base class for Fields.'''

    # Default variable delimiter
    _mark = MARK
    
    def __init__(self, name, auto=True, omax=25, **kw):
        '''
        @param src Field name
        @param auto Turns automagic on and off (default: True)
        @param omax Maximum number of times a field can repeat (default: 25)
        '''
        super(_TextField, self).__init__(auto, omax, **kw)
        self.__name__ = name
        # Set text to empty unicode string
        self.text = self._btext = u''

    def __iadd__(self, data):
        '''Inserts a string or another Template's strings after the internal
        string and the Field (self) is returned modified.
        '''
        # Process strings
        if isinstance(data, basestring):
            # Insert into sibling tracking list
            self._siblings.append(data)
        # Process Templates
        elif hasattr(data, 'mark'):
            # Append rendered string of other Templates
            self._siblings.append(data.render())
        else:
            raise TypeError(_exceptions[2])
        return self

    def render(self, info=None, format='text', encoding='utf-8'):
        '''Returns a string version of this Field.

        @param info Data to substitute into a template (default: None)
        @param format Text format (default: 'text')
        @param encoding Encoding of eturn string (default: 'utf-8')
        '''
        if info is not None: self.__imod__(info)
        # Join internal text with any sibling text
        self.text = u''.join([self.text, u''.join(self._siblings)])
        # Return with encoding
        return self.text.encode(encoding)   

    def reset(self, **kw):
        '''Returns a Template object to its default state.'''
        self.__init__(self.__name__, self._auto, self.max)

    # Sets the delimiter for template variables
    mark = property(lambda self: self._mark, _Field._setmark) 
    # Create property that returns the default Template state
    default = property(lambda self: _TextField(self.__name__, self._auto, self.max))


class _TextMany(object):

    '''Base class for text root and group Templates.'''

    # Variable and group delimiters
    _mark, _groupmark = MARK, GROUPMARK
    
    def __init__(self, auto, omax, **kw):
        super(_TextMany, self).__init__(auto, omax, **kw)
        # Assign match object to internal reference
        self._match = _match

    def __delattr__(self, attr):
        '''Delete a _TextMany attribute.'''
        try:
            # Try removing field
            try:
                # Delete from internal field dictionary
                obj = self._fielddict.pop(attr)
                # Get object's index
                index = self._fields.index(obj)
                # Remove from internal field list
                self._fields.remove(obj)                
                splits, cnt = self._template.split('%s'), 0
                # Remove '%s' from template string
                for idx, item in enumerate(splits):
                    # Find a split point
                    if item.rstrip() == u'':
                        # Find the corresponding split point
                        if cnt == index:
                            # Remove the split point and break
                            del splits[idx]
                            break
                        # Increment separate counter
                        cnt += 1
                # Recreate internal template
                self._template = '%s'.join(splits)
            except KeyError: pass
        # Always delete object attribute if set
        finally:
            if hasattr(self, attr): object.__delattr__(self, attr)         

    def _addfield(self, name):
        '''Adds a field from an element.'''
        # Check if processed already
        if name not in self._filter:
            # Add to filter list if unprocessed
            self._filter.add(name)
            # Add child as field
            self._setfield(name, _TextField(name, self._auto, self._max))            

    def render(self, info=None, format='text', encoding='utf-8'):
        '''Returns the string version of the internal template's current state.

        @param info Data to substitute into internal template (default: None)
        @param format Format of document (default:'text')
        @param encoding Encoding type for output string (default: 'utf-8')        
        '''
        if info is not None: self.__imod__(info)
        # Render internal fields and store in tuple
        content = tuple(i.render(None, format, encoding) for i in self._fields)
        # Interpolate into template
        self._text = self._template % content
        # Output w/ correct encoding
        return self._text.encode(encoding)            

    def reset(self, **kw):
        '''Returns a Template object to its default state.'''
        self.__init__(self._btext, self._auto, self._max)   
    

class _TextGroup(_TextMany, _Group, _NonRoot):

    '''Class for text group Templates.'''

    def __init__(self, src=None, auto=True, omax=25, **kw):
        '''
        @param src Template string (default: None)
        @param auto Turns automagic on and off (default: True)
        @param omax Maximum number of times a group can repeat (default: 25)
        '''
        super(_TextGroup, self).__init__(auto, omax, **kw)
        # Internal temp field tracker and temp template
        self._tempfields, self._ttemplate = list(), ''
        if src is not None: self._settemplate(src)

    def __iadd__(self, data):
        '''Inserts a string or another Template's strings after the internal
        string and the Template (self) is returned modified.
        '''
        # Process strings
        if isinstance(data, basestring):
            # Append string onto internal template
            self._template = u''.join([self._template, data])
        # Process Templates
        elif hasattr(data, 'mark'):
            if hasattr(data, 'groupmark'):
                # Add group-like Template fields to _tempfield tracker
                self._tempfields.extend(data._fields)
                # Add group-like Template's template to temporary template
                self._ttemplate = u''.join([self._ttemplate, data._template])
            else:
                # Add fields to _tempfield tracker
                self._tempfields.append(data)
                # Add delimiter onto temp template
                self._ttemplate = u''.join([self._ttemplate, '%s'])
        else:
            raise TypeError(_exceptions[2])
        return self

    def __deepcopy__(self, memo):
        # Python 2.4 deepcopy copies regexes while Python 2.5 does not
        idict = self.__dict__
        # Remove _match regex if present
        try:
            match = idict.pop('_match')
        # Use global if object does not have _match attribute
        except KeyError:
            match = _match
        # Deep copy original object's __dict__
        ndict = deepcopy(idict)
        # Re-add _match object
        ndict['_match'] = match
        # Create blank group Template
        cls = _TextGroup()
        # Update with self's dictionary
        cls.__dict__.update(ndict)
        return cls

    def _changematch(self):
        '''Changes the delimiter regex pattern.'''
        self._match = getpattern(self._mark, self._groupmark)
        # Change delimiter on children
        for field in self._fields:
            if hasattr(field, 'groupmark'): field._match = self._match

    def _setgmark(self, mark):
        '''Sets the group delimiter for the Template and its children.'''
        super(_TextGroup, self)._setgmark(mark)
        self._changematch()
        
    def _setmark(self, mark):
        '''Sets the variable delimiter for the Template and its children.'''
        super(_TextGroup, self)._setmark(mark)
        self._changematch()

    def _settemplate(self, instr):
        '''Sets the internal group template.'''
        # Iterate over any found fields
        for mo in self._match.finditer(instr):
            first, second = mo.groups()
            # Extract field if found
            if second is not None: self._addfield(second)
        # Check if field is empty
        if self._fields:
            # Create internal template
            self._template = self._match.sub('%s', instr)
            # Create text stubs and backup text
            self._text, self._btext = u'', instr

    def render(self, info=None, format='text', encoding='utf-8'):
        '''Returns the string version of the internal template's current state.

        @param info Data to substitute into internal template (default: None)
        @param format Format of document (default:'text')
        @param encoding Encoding type for output string (default: 'utf-8')        
        '''
        # Run superclass render
        text = super(_TextGroup, self).render(info, format, encoding)
        # Render any tempfield siblings and store in tuple
        content = tuple(i.render(None, format, encoding) for i in self._tempfields)
        # Join existing content with temporary content
        self._text = u''.join([text, self._ttemplate % content])
        # Return with correct encoding
        return self._text.encode(encoding)  

    # Sets the delimiter for template variables
    mark = property(lambda self: self._mark, _setmark)
    # Sets the delimiter for template groups
    groupmark = property(lambda self: self._groupmark, _setgmark)  
    # Create property that returns the default Template state
    default = property(lambda self: _TextGroup(self._btext, self._auto, self._max))
    

class TextTemplate(_TextMany, _Template):

    '''Text root Template class.'''

    __name__ = 'root'
    # Pattern to split group name from group template
    _groupbr = re.compile('(\w+)(\W.+)', re.DOTALL|re.UNICODE)

    def __init__(self, src=None, auto=True, omax=25, **kw):
        '''
        @param src Path or string source (default: None)
        @param auto Turns automagic on or off (default: True)
        @param omax Max number of times a Template can repeat (default: 25)
        '''
        super(TextTemplate, self).__init__(auto, omax, **kw)
        # Check if source exists
        if src is not None:
            # Try reading text source from a file
            try:
                self.fromfile(src)
            except IOError:
                # Try reading from a string
                try:
                    self.fromstring(src)
                except SyntaxError:
                    raise IOError(_exceptions[1])

    def __iadd__(self, data):
        '''Inserts a string or another Template's strings after the internal
        string and the Template (self) is returned modified.
        '''
        # Process strings
        if isinstance(data, basestring):
            # Append string to internal template
            self._template = u''.join([self._template, data])
        # Process Templates
        elif hasattr(data, 'mark'):
            if hasattr(data, 'groupmark'):
                # Extend internal fields with other Template's fields
                self._fields.extend(data._fields)
                # Append other Template's internal template
                self._template = u''.join([self._template, data._template])
            else:
                # Append field to internal field list
                self._fields.append(data)
                # Append delimiter to internal template
                self._template = u''.join([self._template, '%s'])
        else:
            raise TypeError(_exceptions[2])
        return self

    def __deepcopy__(self, memo):
        '''Customizes deep copies w/ 'deepcopy'.'''
        # Python 2.4 deepcopy copies regex objects while Python 2.5 does not
        idict = self.__dict__
        # Remove _match regex if present
        try:
            match = idict.pop('_match')
        # Use global if object does not have _match attribute
        except KeyError:
            match = _match
        # Deep copy original object's __dict__
        ndict = deepcopy(idict)
        # Re-add _match object
        ndict['_match'] = match
        # Create blank group Template
        cls = _TextGroup()
        # Update with deepcopied dictionary
        cls.__dict__.update(ndict)
        # Return copied class
        return cls  

    def _addgroup(self, group):
        '''Creates group Templates.'''
        # Separate group name and template
        realname, template = self._groupbr.match(group).groups()
        name = _checkname(realname)
        # Check if group already processed
        if name not in self._filter:
            # Mark as processed
            self._filter.add(name)
            # Make new group Template w/o passing child
            node = _TextGroup(template, self._auto, self._max)
            # Name group
            node.__name__ = name
            # Set field
            self._setfield(name, node)

    def _setgmark(self, mark):
        '''Sets the group delimiter for the Template and its children.'''
        super(TextTemplate, self)._setgmark(mark)
        self._changematch()
        
    def _setmark(self, mark):
        '''Sets the variable delimiter for the Template and its children.'''
        super(TextTemplate, self)._setmark(mark)
        self._changematch()

    def fromfile(self, path):
        '''Creates an internal element from a file source.

        @param path Path to source
        '''
        self.fromstring(open(path, 'rb').read())

    def fromstring(self, instr):
        '''Creates an internal template from a string source.

        @param instr String source
        '''
        # Extract fields, groups from source
        for mo in self._match.finditer(instr):
            first, second = mo.groups()
            # Add groups
            if first is not None:
                self._addgroup(first)
            # Add fields
            elif second is not None:
                self._addfield(second)
        # Only initialize Template's w/ fields
        if self._fields:
            # Create internal template
            self._template = self._match.sub(u'%s', instr)
            # Create text stub and backup text
            self._text, self._btext = u'', instr

    # Sets the delimiter for template variables
    mark = property(lambda self: self._mark, _setmark)
    # Sets the delimiter for template variables
    groupmark = property(lambda self: self._groupmark, _setgmark)
    # Create property that returns the current Template state   
    current = property(lambda self: deepcopy(self))
    # Create property that returns the default Template state
    default = property(lambda self: TextTemplate(self._btext, self._auto, self._max))


class WSGITextTemplate(WSGIBase):

    '''WSGI middleware for using TextTemplate to render web content.'''

    _format, _klass = 'text', TextTemplate    