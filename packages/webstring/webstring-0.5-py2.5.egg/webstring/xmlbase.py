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

'''XML template base.'''

import random as _random
import md5 as _md5
from sys import maxint as _maxint
from random import randint as _randint
# Python 2.5 import
try:
    from xml.etree.ElementTree import Element
# non-Python 2.5 import
except ImportError:
    from elementtree.ElementTree import Element
from webstring.base import _checkname, _Template, _Group, _Field, _exceptions, _Stemplate

__all__ = ['_XMLTemplate', '_XMLGroup', '_XMLOne', '_XMLField', '_copytree']

def _copytree(tree):
    '''Copies an element.'''
    element = tree.makeelement(tree.tag, tree.attrib)
    element.tail, element.text = tree.tail, tree.text
    for child in tree: element.append(_copytree(child))
    return element

def _copyetree(tree, builder):
    '''Copies an element to a different ElementTree implementation.'''
    element = builder(tree.tag, dict(tree.attrib.iteritems()))
    element.tail, element.text = tree.tail, tree.text
    for child in tree: element.append(_copyetree(child, builder))
    return element

_random.seed()


class _XMLMany(object):

    '''Base class for XML Templates with subtemplates.'''

    # XML attribute indicating fields and groups 
    _mark, _groupmark  = 'id', 'class'

    def __delattr__(self, attr):
        '''Delete an attribute.'''
        try:
            # Try removing field from _XMLMany
            try:
                # Delete from internal field dictionary
                obj = self._fielddict.pop(attr)
                # Remove from internal field list
                self._fields.remove(obj) 
                # Remove internal element from parent
                obj._parent.remove(obj._tree)
            except KeyError: pass
        # Always delete object attribute
        finally:
            if hasattr(self, attr): object.__delattr__(self, attr)

    def _addfield(self, child, parent):
        '''Adds a field from an element.'''
        # If element has variable delimiter, make field
        name = _checkname(child.attrib[self._mark])
        # Check if processed already
        if name not in self._filter:
            # Add to filter list if unprocessed
            self._filter.add(name)
            # Add child as field
            self._setfield(name, self._field(child, parent, self._auto, self._max))

    def _delgmark(self):
        '''Removes group delimiter attribute.'''
        for field in self._fields:
            if hasattr(field, 'groupmark'): del field.groupmark

    def _delmark(self):
        '''Removes variable delimiter attribute.'''
        for field in self._fields: del field.mark             
                
    def templates(self, tempdict):
        '''Sets inline text and attribute templates for child fields.

        @param tempdict Dictionary of templates        
        '''        
        if isinstance(tempdict, dict):
            # Make sure there are no more templates than there are fields
            if len(tempdict) <= len(self):
                self._templates = tempdict
                for key, value in tempdict.iteritems():
                    item = self._fielddict[key]
                    # Handle groups
                    if isinstance(item, _XMLGroup):
                        item.templates(value)
                    # Handle fields
                    elif not hasattr(item, 'groupmark'):
                        # Check if text template is in dict
                        try:
                            item.template = value['text']                            
                        except KeyError: pass
                        # Check if attribute template is in dict
                        try:
                            item.atemplates(value['attrib'])
                        except KeyError: pass
            # Raise exception if more templates than fields
            else:
                raise TypeError('template count exceeds field count')
        else:
            raise TypeError('invalid source for templates')   


class _NonRoot(object):

    '''Base class for non-root XML templates.'''

    def __iadd__(self, data):
        '''Inserts an element or another Template's elements after the internal
        element and this Template (self) is returned modified.
        '''
        # Process Templates
        if hasattr(data, 'mark'):
            # Get fresh copy of data (needed for lxml compatibility)
            if data._parent is not None: data = data.current
            # Add to _tempfields
            self._tempfields.append(data)
            # Make Template's internal tree the data
            data = data._tree
        # Process elements
        if hasattr(data, 'tag'):
            # Insert element after internal element + self._siblings length
            self._parent.insert(self._index + len(self._siblings), data)
            # Insert into sibling tracking list
            self._siblings.append(data)
        else:
            raise TypeError(_exceptions[2])
        return self
    
    def _getcurrent(self, call, **kw):
        '''Property that returns the current state of this Field.'''
        newparent, tfield = _copytree(self._parent), list()
        # Sibling elements
        sibs = newparent[self._index:self._index+len(self._siblings)]
        # Copy fields based on any new sibling elements
        for sib in sibs:
            # Try making a field
            try:
                tfield.append(self._field(sib, newparent, self._auto, self.max))
            except KeyError:
                # Try making a group
                try:
                    tfield.append(self._group(sib, newparent, self._auto, self.max))
                except KeyError: pass
        # Internal elements and siblings for new Field come from copy of parent
        return call(newparent[self._index-1], newparent, self._auto, self.max, 
            siblings=sibs, tempfield=tfield, **kw)

    def _getdefault(self, call, **kw):
        '''Property that returns the default state of self.'''
        return call(_copytree(self._btree), None, self._auto, self.max, **kw)

    @property
    def _index(self):
        '''Returns the index under the parent after the internal element.'''
        try:
            return self._idx
        # Store index
        except AttributeError:
            self._idx = self._parent.getchildren().index(self._tree) + 1
            return self._idx      

    def append(self, data):        
        '''Makes an element or another Template's elements children of this
        Template's internal element.

        @param data Template or element
        '''
        # Process elements
        if hasattr(data, 'tag'):
            # Make element child of internal element
            self._tree.append(data)
        # Process Templates
        elif hasattr(data, 'mark'):
            # Make the other Template's children children of internal element
            self._tree.append(data._tree)
            self._tempfields.append(data)
        else:
            raise TypeError(_exceptions[2])

    def render(self, info=None, format='xml', encoding='utf-8'):
        '''Returns a string version the internal element's parent.

        @param info Data to substitute into a document (default: None)
        @param format Format of document (default:'xml')
        @param encoding Encoding type for return string (default: 'utf-8')
        '''
        tostring = self._etree.tostring
        if info is not None: self.__imod__(info)
        # Build up list of strings from internal element and newer siblings
        output = [tostring(self._tree, encoding)]
        output.extend(tostring(f, encoding) for f in self._siblings)
        return ''.join(output)

    def reset(self, **kw):
        '''Returns a Template object to its default state.'''
        # Remove any new siblings        
        for item in self._siblings: self._parent.remove(item)        
        # Save current internal element and its index
        tree, idx = self._tree, self._index
        # Re-initialize self
        self.__init__(self._btree, self._parent, self._auto, self.max, **kw)
        # Insert the new internal element
        self._parent.insert(idx, self._tree)
        # Remove the old internal element
        self._parent.remove(tree)


class _XMLOne(_Field, _NonRoot):

    '''Base class for XML template fields.'''

    # Attribute indicating fields
    _mark = 'id'    
    
    def __init__(self, src, parent=None, auto=True, omax=25, **kw):
        '''Initialization method for fields.
        
        @param src Element source
        @param par Parent element of the source (default: None)
        @param auto Turns automagic on and off (default: True)
        @param omax Maximum number of times a field can repeat (default: 25)
        '''
        super(_XMLOne, self).__init__(auto, omax, **kw)
        # Parent and inline text template
        self._parent, self._template = parent, kw.get('template')
        # Attribute templates
        self._tattrib = kw.get('tattrib', dict())
        if hasattr(src, 'tag'): self._setelement(src)

    def __imod__(self, data):
        '''Substitutes text data into the internal element's text and
        attributes and this field (self) is returned modified.
        '''        
        if isinstance(data, dict):
            # Try popping templates
            try:
                txt = data.pop('template') 
                # Try popping inline text template
                try:
                    self.template = txt.pop('text')
                except KeyError: pass
                # Try popping attribute templates
                try:
                    self.atemplates(txt.pop('attrib'))
                except KeyError: pass
            except KeyError: pass        
            # Try popping attribute content
            try:               
                self.update(data.pop('attrib'))
            except KeyError: pass
        # Run superclass method
        return super(_XMLOne, self).__imod__(data)
        
    def __getitem__(self, key):
        '''Returns the attribute with the given key.'''
        return self._attrib[key]
        
    def __setitem__(self, key, value):
        '''Sets the XML attribute at the given key.'''
        # Set attribute property if automagic on
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self._setattr(key, value)
        
    def __delitem__(self, key):
        '''Deletes an XML attribute.'''
        # Delete the property if automagic on
        try:
            delattr(self, _checkname(key))
        except AttributeError:
            del self._attrib[key]
        # Remove any template for the attribute
        try:
            self._tattrib.pop(key)
        except (AttributeError, KeyError): pass

    def __contains__(self, key):
        '''Tells if an XML attribute is in a field.'''
        return key in self._attrib        

    def __len__(self):
        '''The number of XML attributes in a field.'''
        return len(self._attrib)    

    def __iter__(self):
        '''An iterator for the internal XML attribute dict.'''
        return iter(self._attrib)

    def _delmark(self):
        '''Removes variable delimiter attribute from output.'''
        self.__delitem__(self.mark)
        for field in self._tempfields: del field.mark    

    def _deltext(self):
        '''Sets internal element's text attribute to None.'''
        self._tree.text = None       
 
    def _setattr(self, key, value):
        '''Sets an attribute of the internal element to a new value.'''
        if isinstance(value, basestring):
            self._tree.set(key, value)
        elif isinstance(value, dict):
            # Try string.Template substitution
            try:
                self._tree.set(key, self._tattrib[key].substitute(value))
            # Try string interpolation
            except AttributeError:
                self._tree.set(key, self._tattrib[key] % value)
        if self._auto:
            name = _checkname(key)
            # Make attribute an attribute of self's superclass if automagic on
            setattr(self.__class__, name, _Attribute(key, name))

    def _setelement(self, tree):
        '''Sets the internal element.'''
        self.__name__ = _checkname(tree.attrib[self.mark])        
        # Set internal element and backup tree
        self._tree, self._btree = tree, _copytree(tree)
        # Make tree attribute dictionary a field attribute
        self._attrib, tattrib = tree.attrib, dict()        
        # If inline text template in tree, assign it to template
        try:
            self.template = tree.text
        except TypeError: pass
        for attr, atext in self._attrib.iteritems():
            # If attribute template text in template source, add to _tattrib
            if '$' in atext or '%' in atext: tattrib[attr] = atext
            # Make XML attrs attributes of self if automagic on & not a mark
            if self._auto and attr != self.mark:
                name = _checkname(attr)
                # Set new class as attribute of self's superclass
                setattr(self.__class__, name, _Attribute(attr, name))
        # Assign any attribute templates        
        if tattrib: self.atemplates(tattrib)

    def _settemplate(self, text):
        '''Sets inline text templates for the internal element.'''        
        if isinstance(text, basestring):
            # Make string.Template instance if delimiter '$' found. 
            if '$' in text:
                self._template = _Stemplate(text)
            # Use standard Python format string if delimiter '%' found
            elif '%' in text:
                self._template = text
            # Raise exception if no delimiter found
            else:
                raise TypeError(_exceptions[8]) 
        else:
            raise TypeError(_exceptions[7])

    def _settext(self, text):
        '''Sets internal element's text attribute.'''
        if isinstance(text, basestring):
            self._tree.text = text
        elif isinstance(text, dict):
            # Try string.Template substitution
            try:
                self._tree.text = self._template.substitute(text)
            # Try string interpolation
            except AttributeError:
                self._tree.text = self._template % text
        else:
            raise TypeError(_exceptions[7])        

    @property
    def current(self):
        '''Property that returns the current state of self.'''
        return self._getcurrent(self._field, template=self._template,
            tattrib=self._tattrib)    

    @property
    def default(self):
        '''Property that returns the default state of self.'''
        return self._getdefault(self._field, template=self._template, 
            tattrib=self._tattrib)           

    def atemplates(self, attr):
        '''Sets templates for the internal element's attributes.'''
        if isinstance(attr, dict):
            tattrib = dict() 
            # Set template for each item in attrib dict
            for key, value in attr.iteritems():
                # Make string.Template instance if delimiter '$' is found 
                if '$' in value:
                    tattrib[key] = _Stemplate(value)
                # Use standard Python format string if delimiter '%' found
                elif '%' in value:
                    tattrib[key] = value
                # Raise exception if no delimiter found
                else:
                    raise TypeError(_exceptions[8])
            # Assign object attribute for attribute template dictionary
            self._tattrib.update(tattrib)
        else:
            raise TypeError(_exceptions[7])

    def purge(self, *attrs):
        '''Removes XML attributes from a field.

        @param attrs Tuple of attributes to remove
        '''
        for item in attrs: self.__delitem__(item)    
        
    def reset(self, **kw):
        '''Returns a Template object to its default state.'''
        super(_XMLOne, self).reset(template=self._template, tattrib=self._tattrib)
        
    def update(self, attr):
        '''Sets an internal element's attributes from a dictionary.

        @param attr Dictionary of attributes
        '''
        if isinstance(attr, dict):
            for key, value in attr.iteritems(): self._setattr(key, value)
        else:
            raise TypeError('invalid attribute source')

    # Template variable delimiter attribute name        
    mark = property(lambda self: self._mark, _Field._setmark, _delmark)
    # Internal element text
    text = property(lambda self: self._tree.text, _settext, _deltext)
    # Internal element text template
    template = property(lambda self: self._template, _settemplate)
    

class _Attribute(object):

    '''Class for manipulating the XML attributes of an internal element.'''    

    __slots__ = '_key', '_name'  

    def __init__(self, key, name):
        '''Initializes an _Attribute object.
        
        @param key Name of _Attribute's attribute
        @param name Name of this _Attribute object
        '''
        self._key, self._name = key, name

    def __repr__(self):
        '''Returns string representation of an XML attribute.'''
        return ''.join(['attribute: ', self._key])

    def __get__(self, inst1, inst2):
        '''Returns value of an XML attribute.'''
        return inst1._attrib[self._key]

    def __set__(self, inst, value):
        '''Sets value of an XML attribute.'''
        inst._setattr(self._key, value)

    def __delete__(self, inst):
        '''Deletes an XML attribute.'''
        # Delete the XML attribute from internal element
        del inst._attrib[self._key]
        # Delete self as attribute of object's superclass
        delattr(inst.__class__, self._name)


class _XMLField(object):

    '''Dispatcher class for XML template fields.''' 
    
    def __new__(cls, *arg, **kw):
        '''Dispatcher method for XML fields.'''        
        c = cls._klass
        c._etree, c._group, c._field = cls._etree, cls._group, cls
        # Make new _XMLOne class if automagic on to avoid attribute property overlap         
        if arg[2]:
            c = type(_md5.new(str(_randint(0, _maxint))).digest(), (c, ),
                dict(c.__dict__))
        return c(*arg, **kw)


class _XMLGroup(_XMLMany, _Group, _NonRoot):

    '''Class for XML group Templates.'''

    def __init__(self, src=None, parent=None, auto=True, omax=25, **kw):
        '''Initialization method for a group Template
        
        @param src Element source (default: None)
        @param parent Parent element of the source (default: None)
        @param auto Turns automagic on and off (default: True)
        @param omax Maximum number of times a field can repeat (default: 25)
        '''
        super(_XMLGroup, self).__init__(auto, omax, **kw)
        self._parent = parent
        if hasattr(src, 'tag'): self._setelement(src)
        self._templates = kw.get('templates')
        if self._templates is not None: self.templates(self._templates)

    @property
    def current(self):
        '''Property that returns the current state of this group.'''
        return self._getcurrent(_XMLGroup, templates=self._templates)

    @property
    def default(self):
        '''Property that returns the default state of this group.'''
        return self._getdefault(_XMLGroup, templates=self._templates) 

    def _delgmark(self):
        '''Removes group mark attribute from output.'''
        del self._tree.attrib[self._groupmark]
        super(_XMLGroup, self)._delgmark()
        # Remove groupmark on any concatentated groups
        for field in self._tempfields:
            if hasattr(field, 'groupmark'): del field.groupmark

    def _delmark(self):
        '''Removes variable mark attribute from output.'''
        super(_XMLGroup, self)._delmark()
        for field in self._tempfields: del field.mark   

    def _setelement(self, tree):
        '''Sets the internal element.'''         
        self.__name__ = _checkname(tree.attrib[self.groupmark])
        # Set internal element and backup tree attributes
        self._tree, self._btree = tree, _copytree(tree)
        # Find fields in group
        for parent in tree.getiterator():
            # Get child, parent pairs
            for child in parent:                
                try:
                    self._addfield(child, parent)
                except KeyError: pass

    def reset(self, **kw):
        '''Resets a group back to its default state.'''
        super(_Group, self).reset(templates=self._templates)                

    # Template variable attribute name
    mark = property(lambda self: self._mark, _Group._setmark, _delmark)
    # Group delimiter attribute name
    groupmark = property(lambda self: self._groupmark, _Group._setgmark, _delgmark)
    

class _XMLTemplate(_XMLMany, _Template):

    '''XML root Template class.'''

    __name__, _parent = 'root', None

    def __init__(self, src=None, auto=True, omax=25, **kw):
        '''
        @param src Path, string, or element source (default: None)
        @param auto Turns automagic on or off (default: True)
        @param omax Max number of times a Template can repeat (default: 25)
        '''
        super(_XMLTemplate, self).__init__(auto, omax, **kw)
        # Process element if source is an element
        if hasattr(src, 'tag'):
            self._setelement(src)
        # Check if source exists
        elif src is not None:
            # Try reading source from a file
            try:
                open(src)
                self.fromfile(src)
            except IOError:
                # Try reading from a string
                try:
                    self.fromstring(src)
                except SyntaxError:
                    raise IOError(_exceptions[1]) 
        # Assign any templates
        self._templates = kw.get('templates')
        if self._templates is not None: self.templates(self._templates)

    def __iadd__(self, data):
        '''Inserts an element or another Template's internal elements after
        the internal element and returns the modified Template (self).

        @param data Template or element
        '''        
        # Process element
        if hasattr(data, 'tag'):
            self._tree.append(data)
        # Process Template
        elif hasattr(data, 'mark'):
            # Make int. element of other Template child of this int. element
            self._tree.append(_copytree(data._tree))
            # Extend Template's internal fields with group Template's fields
            if hasattr(data, 'groupmark'):
                self._fields.extend(data._fields)
            # Append standalone fields to Template's field's
            else:
                self._fields.append(data)           
        else:
            raise TypeError(_exceptions[2])        
        return self

    def __getstate__(self):
        '''Prepares a Template for object serialization.'''
        # Convert internal and backup elements to pure Python element trees
        return dict(tree=_copyetree(self._tree, Element), _mark=self.mark,
            btree=_copyetree(self._btree, Element), _templates=self._templates,
             _groupmark=self.groupmark, _auto=self._auto, _max = self._max)            

    def __setstate__(self, s):
        '''Restores a Template from object serialization.'''
        # Recreate internal trackers
        self._fielddict, self._fields, self._filter = dict(), list(), set()
        # Convert old tree and backup tree to cElementTrees
        tree = _copyetree(s.pop('tree'), self._etree.Element)
        btree = _copyetree(s.pop('btree'), self._etree.Element)
        # Update internal dictionary
        self.__dict__.update(s)
        # Recreate tree
        self._setelement(tree)
        # Reassign backuptree
        self._btree = btree
        # Reprocess templates
        if self._templates is not None: self.templates(self._templates)        

    def _addgroup(self, child, parent):
        '''Creates group Templates.'''
        # Verify element is a group element
        realname = child.attrib[self._groupmark]
        name = _checkname(realname)
        # Check if group already processed
        if name not in self._filter:
            # Mark as processed
            self._filter.add(name)
            # Extract any groups under the group's element
            for element in child:
                try:
                    self._addgroup(element, child)
                except KeyError: pass   
            # Make new group Template w/o passing group's element to __init__
            node = self._group(None, parent, self._auto, self._max)       
            # Add self's filter to avoid duplicate children
            node._filter = self._filter
            # Process group's element
            node._setelement(child)
            # Only attach groups with children to root Template
            if len(node): self._setfield(name, node)

    def _setelement(self, tree):
        '''Sets the internal element.''' 
        # Set internal element and backup element
        self._tree, self._btree = tree, _copytree(tree)
        # Find fields and groups
        for parent in tree.getiterator():
            for child in parent:
                # Try making child a field
                try:                    
                    self._addfield(child, parent)
                except KeyError:
                    # Try making child a group
                    try:
                        self._addgroup(child, parent)
                    except KeyError: pass

    def _setgmark(self, mark):
        '''Sets the groupmark for a group or root.'''
        super(_Template, self)._setgmark(mark)
        # Set mark on all child Groups
        for field in self._fields:
            if hasattr(field, 'groupmark'): field.groupmark = mark                    

    def fromfile(self, path):
        '''Creates an internal element from a file source.

        @param path Path to template source
        '''
        self._setelement(self._etree.parse(path).getroot())

    def fromstring(self, instring):
        '''Creates an internal element from a string source.

        @param instring String source for internal element
        '''
        self._setelement(self._etree.XML(instring))

    def render(self, info=None, format='xml', encoding='utf-8'):
        '''String version of the internal element.

        @param info Data to substitute into an XML document (default: None)
        @param format Format of document (default: 'xml')
        @param encoding Encoding type for return string (default: 'utf-8')
        '''
        if info is not None: self.__imod__(info)
        return self._etree.tostring(self._tree, encoding)

    def reset(self):
        '''Returns a Template object to its default state.'''
        self.__init__(self._btree, self._auto, self._max, templates=self._templates)

    # Template variable attribute name        
    mark = property(lambda self: self._mark, _Template._setmark, _XMLMany._delmark)
    # Group delimiter attribute name
    groupmark = property(lambda self: self._groupmark, _Template._setgmark, _XMLMany._delgmark)