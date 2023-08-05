#! /usr/bin/env python

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

'''Unit tests for lwebstring'''

import unittest
import pickle
try:
    import lxml.etree as _etree  
except ImportError:
    raise ImportError(_exceptions[6])
_Element = _etree.Element
from webstring import *

class Testwebstring(unittest.TestCase):

    '''Test class for webstring'''     

    # Add tests        
    groupend = '<tr class="tr1"><td id="td1"/><td id="td2"/>' \
        '</tr><tr class="tr2"><td id="td1"/><td id="td2"/></tr>'
    altgroupend = '<tr class="tr2"><td id="td1"/>' \
        '<td id="td2"/></tr><tr class="tr1"><td id="td1"/>' \
        '<td id="td2"/></tr>'
    subgroupend = '<td id="td1"/><td id="td1"/>'        
    addtest = '<html><head><title id="title"/></head><html><body>' \
        '<p id="content"/></body></html></html>'
    altaddtest = '<html><body><p id="content"/></body><head>' \
        '<title id="title"/></head></html>'        
    field_add = '<p id="content"/><title id="title"/>'
    field_group_add = '<title id="title"/><tr class="tr1"><td id="td1"/>' \
        '<td id="td2"/></tr>'
    root_group_add = '<html><head><title id="title"/></head>' \
        '<tr class="tr1"><td id="td1"/><td id="td2"/></tr></html>'
    root_element_add = '<html><head><title id="title"/></head><p/>' \
        '</html>'
    field_element_add = '<title id="title"/><p/>'
    group_element_add = '<tr class="tr1"><td id="td1"/>' \
        '<td id="td2"/></tr><p/>'
    subfield_element_add = '<td id="td1"/><p/>'
    # Mul tests
    multest = '<p id="content"/><p id="content"/><p id="content"/>'
    root_mul = '<html><head><title id="title"/></head><html><body>' \
        '<p id="content"/></body></html><html><head><title id="title"/>' \
        '</head><html><body><p id="content"/></body></html></html><html>' \
        '<head><title id="title"/></head><html><body><p id="content"/>' \
        '</body></html></html></html>'
    root_group_mul = '<tr class="tr1"><td id="td1"/>' \
        '<td id="td2"/></tr><tr class="tr1"><td id="td1"/>' \
        '<td id="td2"/></tr><tr class="tr1"><td id="td1"/>' \
        '<td id="td2"/></tr>'
    subfield_group_mul = '<td id="td1"/><td id="td1"/><td id="td1"/>'
    # Mod tests
    modtest1 = '<html><head><title id="title">Test Page</title>' \
        '</head><body/></html>'        
    modtest2 = '<html><head><title id="title">Test Page</title></head>' \
    '<html><body><p id="content">Content Goes Here</p></body></html></html>'
    modtest3 = '<html><head><title id="title">Title</title></head>' \
        '<body><p id="content">Test1</p><p id="content">Test2</p>' \
        '<p id="content2">Test1</p><p id="content2">Test2</p>' \
        '</body></html>'
    modtest5 = '<title id="title">Test Page</title>'
    groupmod = '<td id="td1">Test Page</td>'
    groupmod2 = '<table><tr class="tr1"><td id="td1">Test Page</td>' \
        '<td id="td2">Content Goes Here</td></tr></table>'
    groupmod3 = '<table><tr class="tr1"><td id="td1">Test1</td><td ' \
        'id="td1">Test2</td><td id="td2">Test1</td><td id="td2">Test2' \
        '</td></tr></table>'
    # Pow tets
    powtest1 = '<p id="content">Test1</p><p id="content">Test2</p>'
    groupow = '<tr class="tr1"><td id="td1">1</td>' \
        '<td id="td2">2</td></tr><tr class="tr1"><td id="td1">3' \
        '</td><td id="td2">4</td></tr><tr class="tr1"><td id="td1">5' \
        '</td><td id="td2">6</td></tr>'
    # Templates
    modtemplate1 = Template('<html><head><title id="title"/></head>' \
        '<body/></html>', engine='lxml')
    modtemplate3 = Template('<html><head><title id="title"></title>' \
        '</head><body><p id="content"/><p id="content2"/></body>' \
        '</html>', engine='lxml')        
    gentemplate = Template(addtest, engine='lxml')
    atemplate = Template('<html><head><title id="title"></title></head>' \
        '</html>', engine='lxml')
    btemplate = Template('<html><body><p id="content"></p></body></html>', engine='lxml')
    powtemplate = Template('<html><head/><body><p id="content"/>' \
        '</body></html>', engine='lxml')
    agrouptest = Template('<table><tr class="tr1"><td id="td1"/>' \
        '<td id="td2"/></tr></table>', engine='lxml')
    bgrouptest = Template('<table><tr class="tr2"><td id="td1"/>' \
        '<td id="td2"/></tr></table>', engine='lxml')
    subcombotest = Template('<body><a id="fieldtest" href="atest"/>' \
        '<tr class="grouptest"><td id="groupfield1"/>' \
        '<td id="groupfield2"/></tr></body>', engine='lxml')
    rss = Template('''<rss version="2.0">
<channel>
<title>Example</title>
<link>http://www.example.org/</link>
<description>RSS Example</description>
<language>en-us</language>
<pubDate id="cpubdate">$month $day, $year</pubDate>
<lastBuildDate id="lastbuilddate">%(month)s %(day)s, %(year)s</lastBuildDate>
<item class="item">
<title id="title"/>
<link id="link"/>
<guid id="guid" isPermaLink="true"/>
<description id="description"/>
<pubDate id="ipubdate"/>
</item>
</channel>
</rss>''', engine='lxml')
    htmlt = HTMLTemplate('<html><head><link href="test.css" ' \
        'type="text/css"><title id="title"><body><p id="content">' \
        '</body></head></html>', engine='lxml')
    # Data structures        
    powdict = {'content1':'Test1', 'content2':'Test2'}
    powtup = ('Test1', 'Test2')
    moddict = {'content':'Content Goes Here', 'title':'Test Page'}
    groupdict = {'td1':'Test Page', 'td2':'Content Goes Here'}
    modtup = ('Test Page', 'Content Goes Here')
    grouptup = (('1', '2'), ('3', '4'), ('5', '6'))
    groupowdict = {'2':['1', '2'], '4':['3', '4'], '6':['5', '6']}       

    def test_lroot_add(self):
        '''Tests addition of two root Templates.'''
        atst = self.atemplate + self.btemplate
        self.assertEqual(self.addtest, atst.render())

    def test_lroot_radd(self):
        '''Tests the right-side addition of two root Templates.'''
        final = '<html><body><p id="content"/></body><html><head>' \
            '<title id="title"/></head></html></html>'
        atst = self.btemplate + self.atemplate
        self.assertEqual(final, atst.render())

    def test_lroot_iadd(self):
        '''Tests the modifying addition of two root Templates.'''
        self.atemplate += self.btemplate
        self.assertEqual(self.addtest, self.atemplate.pipe())

    def test_lfield_add(self):
        '''Tests the addition of two fields.'''
        final = '<title id="title"/><p id="content"/>'
        atst = self.atemplate.title + self.btemplate.content
        self.assertEqual(final, atst.render())

    def test_lfield_radd(self):
        '''Tests the right-side addition of two fields.'''
        atst = self.btemplate.content + self.atemplate.title
        self.assertEqual(self.field_add, atst.render())

    def test_lfield_iadd(self):
        '''Tests the modifying addition of two fields.'''
        self.btemplate.content += self.atemplate.title
        self.assertEqual(self.field_add, self.btemplate.content.pipe())

    def test_lgroup_add(self):
        '''Tests the addition of two groups.'''
        atst = self.agrouptest.tr1 + self.bgrouptest.tr2
        self.assertEqual(self.groupend, atst.render())

    def test_lgroup_radd(self):
        '''Tests the right-side addition of two groups.'''
        atst = self.bgrouptest.tr2 + self.agrouptest.tr1
        self.assertEqual(self.altgroupend, atst.render())

    def test_lgroup_iadd(self):
        '''Tests the modifying addition of two groups.'''
        self.agrouptest.tr1 += self.bgrouptest.tr2
        self.assertEqual(self.groupend, self.agrouptest.tr1.pipe())

    def test_lsubfield_add(self):
        '''Tests the addition of two subfields.'''
        atst = self.agrouptest.tr1.td1 + self.bgrouptest.tr2.td1
        self.assertEqual(self.subgroupend, atst.render())

    def test_lsubfield_radd(self):
        '''Tests the right-side addition of two subfields.'''
        final = '<td id="td1"/><td id="td1"/>'
        atst = self.bgrouptest.tr2.td1 + self.agrouptest.tr1.td1
        self.assertEqual(final, atst.render())

    def test_lsubfield_iadd(self):
        '''Tests the modifying addition of two subfields.'''
        self.agrouptest.tr1.td1 += self.bgrouptest.tr2.td1
        self.assertEqual(self.subgroupend, self.agrouptest.tr1.td1.pipe())

    def test_lfield_root_iadd(self):
        '''Tests the modifying addition of a field and a root Template.'''
        final = '<title id="title"/><html><body><p id="content"/>' \
            '</body></html>'
        self.atemplate.title += self.btemplate
        self.assertEqual(final, self.atemplate.title.pipe())

    def test_lfield_group_iadd(self):
        '''Tests the modifying addition of a field and group.'''
        self.atemplate.title += self.agrouptest.tr1
        self.assertEqual(self.field_group_add,
            self.atemplate.title.pipe())

    def test_lfield_subfield_iadd(self):
        '''Tests the modifying addition of a field and subfield.'''
        final = '<title id="title"/><td id="td1"/>'
        self.atemplate.title += self.agrouptest.tr1.td1
        self.assertEqual(final, self.atemplate.title.pipe())                

    def test_lroot_field_iadd(self):
        '''Tests the modifying addition of a root Template and a field.'''
        final = '<html><body><p id="content"/></body>' \
        '<title id="title"/></html>'
        self.btemplate += self.atemplate.title
        self.assertEqual(final, self.btemplate.pipe())

    def test_lroot_group_iadd(self):
        '''Tests the modifying addition of a root Template and a group.'''
        self.atemplate += self.agrouptest.tr1
        self.assertEqual(self.root_group_add, self.atemplate.pipe())

    def test_lroot_subfield_iadd(self):
        '''Tests the modifying addition of a root Template and subfield.'''
        final = '<html><head><title id="title"/></head><td id="td1"/></html>'
        self.atemplate += self.agrouptest.tr1.td1
        self.assertEqual(final, self.atemplate.pipe())

    def test_lgroup_subfield_iadd(self):
        '''Tests the modifying addition of one group and one subfield.'''
        final = '<tr class="tr1"><td id="td1"/><td id="td2"/>' \
            '</tr><td id="td1"/>'
        self.agrouptest.tr1 += self.bgrouptest.tr2.td1
        self.assertEqual(final, self.agrouptest.tr1.pipe())

    def test_lsubfield_group_iadd(self):
        '''Tests the modifying addition of one subfield and one group.'''
        final = '<td id="td1"/><tr class="tr1">' \
            '<td id="td1"/><td id="td2"/></tr>'
        self.bgrouptest.tr2.td1 += self.agrouptest.tr1
        self.assertEqual(final, self.bgrouptest.tr2.td1.pipe())            

    def test_lroot_element_radd(self):
        '''Tests the right-side addition of a root Template and an Element.'''
        atst = _Element('p') + self.atemplate
        self.assertEqual(self.root_element_add, atst.render())

    def test_lroot_element_iadd(self):
        '''Tests the modifying addition of a root Template and an Element.'''
        self.atemplate += _Element('p')
        self.assertEqual(self.root_element_add, self.atemplate.pipe())

    def test_lfield_element_radd(self):
        '''Tests the right-side addition of a field and an Element.'''
        atst = _Element('p') + self.atemplate.title
        self.assertEqual(self.field_element_add, atst.render())

    def test_lfield_element_iadd(self):
        '''Tests the modifying addition of a field and an Element.'''
        self.atemplate.title += _Element('p')
        self.assertEqual(self.field_element_add,
            self.atemplate.title.pipe())

    def test_lgroup_element_radd(self):
        '''Tests the right-side addition of a group and an Element.'''
        atst = _Element('p') + self.agrouptest.tr1
        self.assertEqual(self.group_element_add, atst.render())

    def test_lgroup_element_iadd(self):
        '''Tests the modifying addition of a group and an Element.'''
        self.agrouptest.tr1 += _Element('p')
        self.assertEqual(self.group_element_add,
            self.agrouptest.tr1.pipe())

    def test_lsubfield_element_radd(self):
        '''Tests the right-side addition of a subfield and an Element.'''
        atst = _Element('p') + self.agrouptest.tr1.td1
        self.assertEqual(self.subfield_element_add, atst.render())

    def test_lsubfield_element_iadd(self):
        '''Tests the modifying addition of a subfield and an Element.'''
        self.agrouptest.tr1.td1 += _Element('p')
        self.assertEqual(self.subfield_element_add,
            self.agrouptest.tr1.td1.pipe())             

    def test_lroot_radd_raise(self):
        '''Raises TypeError if wrong type right-side added to root Template.'''
        def tempfunc(): return [1, 1, 1] + self.atemplate
        self.assertRaises(TypeError, tempfunc)

    def test_lroot_iadd_raise(self):
        '''Raises TypeError if wrong type is added to root Template.'''
        def tempfunc():
            atst = self.atemplate.default
            atst += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)

    def test_lfield_radd_raise(self):
        '''Raises TypeError if wrong type is right-side added to field.'''
        def tempfunc():
            return [1, 1, 1] + self.atemplate.title
        self.assertRaises(TypeError, tempfunc)

    def test_lfield_iadd_raise(self):
        '''Raises TypeError if wrong type is modifyingly added to field.'''
        def tempfunc():
            atst = self.atemplate.default
            atst.title += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_radd_raise(self):
        '''Raises TypeError if wrong type is right-side added to group.'''
        def tempfunc(): return [1, 1, 1] + self.agrouptest.tr1
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_iadd_raise(self):
        '''Raises TypeError if wrong type is modifyingly added to group.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1 += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)

    def test_lsubfield_radd_raise(self):
        '''Raises TypeError if wrong type is right-side added to subfield.'''
        def tempfunc(): return [1, 1, 1] + self.agrouptest.tr1.td1
        self.assertRaises(TypeError, tempfunc)

    def test_lsubfield_iadd_raise(self):
        '''Raises TypeError if wrong type is modifyingly added to subfield.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.td1 += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)    

    def test_lroot_rmul(self):
        '''Tests repetition of a root Template with number on the right.'''
        atst = 3 * self.gentemplate
        self.assertEqual(self.root_mul, atst.render())

    def test_lroot_imul(self):
        '''Tests modifying repetition of a root Template.'''
        self.gentemplate *= 3            
        self.assertEqual(self.root_mul, self.gentemplate.pipe())

    def test_lfield_mul(self):
        '''Tests the repetition of a field.'''
        atst = self.gentemplate.content * 3
        self.assertEqual(self.multest, atst.render())

    def test_lfield_rmul(self):
        '''Tests repetition of a field with the number on the right.'''
        atst = 3 * self.gentemplate.content
        self.assertEqual(self.multest, atst.render())

    def test_lfield_imul(self):
        '''Tests modifying repetition of a field.'''
        self.gentemplate.content *= 3
        self.assertEqual(self.multest, self.gentemplate.content.pipe())        

    def test_lgroup_rmul(self):
        '''Tests repetition of a group with the number on the right side.'''
        atst = 3 * self.agrouptest.tr1
        self.assertEqual(self.root_group_mul, atst.render())

    def test_lgroup_imul(self):
        '''Tests modifying repetition of a group.'''
        self.agrouptest.tr1 *= 3            
        self.assertEqual(self.root_group_mul, self.agrouptest.tr1.pipe())

    def test_lsubfield_rmul(self):
        '''Tests repetition of a subfield with the number on the right side.'''
        atst = 3 * self.agrouptest.tr1.td1
        self.assertEqual(self.subfield_group_mul, atst.render())

    def test_lsubfield_mul(self):
        '''Tests the repetition of a subfield.'''
        atst = self.agrouptest.tr1.td1 * 3
        self.assertEqual(self.subfield_group_mul, atst.render())    

    def test_lsubfield_imul(self):
        '''Tests modifying repetition of a subfield.'''
        self.agrouptest.tr1.td1 *= 3            
        self.assertEqual(self.subfield_group_mul,
            self.agrouptest.tr1.td1.pipe())

    def test_lfield_imul_rep(self):
        '''Tests restraint on a max modifying repetition of a field.'''
        def tempfunc():
            atst = self.gentemplate.default
            atst.content.max = 2
            atst.content *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_lroot_imul_rep(self):
        '''Tests restraint on max modifying repetition of a root Template.'''
        def tempfunc():
            atst = self.gentemplate.default
            atst.max = 2
            atst *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_imul_rep(self):
        '''Tests restraint on max modifying repetition of a field.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.max = 2
            atst.tr1 *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_lsubfield_imul_rep(self):
        '''Tests restraint on max modifying repetition of a subfield.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.td1.max = 2
            atst.tr1.td1 *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_lfield_string_mod(self):
        '''Tests a modifying string substitution of a field.'''
        atst = self.modtemplate1.title % 'Test Page'
        self.assertEqual(atst.render(), self.modtest5)

    def test_lfield_string_imod(self):
        '''Tests a modifying string substitution of a field.'''
        self.modtemplate1.title %= 'Test Page'
        self.assertEqual(self.modtest5, self.modtemplate1.title.pipe())

    def test_lsubfield_string_imod(self):
        '''Tests a modifying string substitution of a subfield.'''
        self.agrouptest.tr1.td1 %= 'Test Page'
        self.assertEqual(self.groupmod, self.agrouptest.tr1.td1.pipe())

    def test_lroot_string_mod(self):
        '''Raises TypeError if string passed to a root Template.'''
        def tempfunc(): return self.gentemplate % 'Test Page'
        self.assertRaises(TypeError, tempfunc)

    def test_lfield_mod_str_wrongtype(self):
        '''Raises TypeError if wrong type passed to a field.'''
        def tempfunc(): return self.gentemplate.content % ['Test Page']
        self.assertRaises(TypeError, tempfunc)            

    def test_lroot_group_str_mod_toofew(self):
        '''Raises TypeError if string passed to root containing only group.'''
        def tempfunc(): return self.agrouptest % 'Test Page'
        self.assertRaises(TypeError, tempfunc)

    def test_lfield_group_str_mod_toofew(self):
        '''Raises TypeError if string passed to a group.'''
        def tempfunc(): return self.agrouptest.tr1 % 'Test Page'
        self.assertRaises(TypeError, tempfunc)        

    def test_lroot_tuple_imod(self):
        '''Tests a modifying tuple substitution of a root Template.'''
        self.gentemplate %= self.modtup
        self.assertEqual(self.modtest2, self.gentemplate.pipe())

    def test_lgroup_tuple_imod(self):
        '''Tests a modifying tuple substitution of a group.'''
        self.agrouptest.tr1 %= self.modtup
        self.assertEqual(self.groupmod2, self.agrouptest.pipe())            

    def test_lroot_tuple_tuple_imod_expand(self):
        '''Tests a modifying tuple tuple substitution/expansion of root.'''
        self.modtemplate3 %= ('Title', ('Test1', 'Test2'),
            ('Test1', 'Test2'))
        self.assertEqual(self.modtest3, self.modtemplate3.pipe())

    def test_lgroup_tuple_tuple_imod_expand(self):
        '''Tests a modifying tuple tuple substitution/expansion of a group.'''
        self.agrouptest.tr1 %= (('Test1', 'Test2'), ('Test1', 'Test2'))
        self.assertEqual(self.groupmod3, self.agrouptest.pipe())

    def test_lroot_tuple_mod_wrongtype(self):
        '''Raises TypeError if wrong type in tuple is subbed into root.'''
        def tempfunc(): return self.gentemplate % (set(['Test Page']), )
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_tuple_mod_wrongtype(self):
        '''Raises TypeError if wrong type in tuple is subbed into group.'''
        def tempfunc(): return self.agrouptest.tr1 % (set(['Test Page']), )
        self.assertRaises(TypeError, tempfunc)            

    def test_lroot_tuple_mod_toomany(self):
        '''Raises TypeError if too many items in tuple are subbed in root.'''
        def tempfunc(): return self.gentemplate % ('Test', 'Test', 'Too Many')
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_tuple_mod_toomany(self):
        '''Raises TypeError if too many items in tuple are subbed in group.'''
        def tempfunc(): return self.agrouptest.tr1 % ('Test', 'Test', 'Test')
        self.assertRaises(TypeError, tempfunc)              

    def test_lroot_tuple_mod_toofew(self):
        '''Raises TypeError if too few items in tuple are subbed into root.'''
        def tempfunc(): return self.gentemplate % ('Test Page')
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_tuple_mod_toofew(self):
        '''Raises TypeError if too few items in tuple are subbed into group.'''
        def tempfunc(): return self.agrouptest.tr1 % ('Test Page')
        self.assertRaises(TypeError, tempfunc)        

    def test_lroot_dict_imod(self):
        '''Tests a modifying dictionary substitution of a root Template.'''
        self.gentemplate %= self.moddict
        self.assertEqual(self.modtest2, self.gentemplate.pipe())

    def test_lgroup_dict_imod(self):
        '''Tests a modifying dict substitution of a group Template.'''
        self.agrouptest.tr1 %= self.groupdict
        self.assertEqual(self.groupmod2, self.agrouptest.pipe())

    def test_lroot_dict_tuple_imod_expand(self):
        '''Tests a modifying dictionary tuple sub/expansion of a root.'''
        self.modtemplate3 %= {'title':'Title', 'content':('Test1', 'Test2'),
            "content2":('Test1', 'Test2')}
        self.assertEqual(self.modtest3, self.modtemplate3.pipe())

    def test_lgroup_dict_tuple_imod_expand(self):
        '''Tests a modifying dict tuple substitution/expansion of a group.'''
        self.agrouptest.tr1 %= {'td1':('Test1', 'Test2'),
            'td2':('Test1', 'Test2')}
        self.assertEqual(self.groupmod3, self.agrouptest.pipe())

    def test_lroot_dict_mod_wrongtype(self):
        '''Raises TypeError if wrong type in a dict are subbed into a root.'''
        def tempfunc(): return self.gentemplate % {'content':set(['Test'])}
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_dict_mod_wrongtype(self):
        '''Raises TypeError if wrong type in a dict are subbed into a group.'''
        def tempfunc(): return self.agrouptest.tr1 % {'td1':set(['Test Page'])}
        self.assertRaises(TypeError, tempfunc)            

    def test_lroot_dict_mod_toomany(self):
        '''Raises TypeError if too many items in dict are subbed into root.'''
        def tempfunc():
            return self.gentemplate % {'content':'Content Goes Here',
                'title':'Test Page', 'test':'Too many'}
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_dict_mod_toomany(self):
        '''Raises TypeError if too many items in dict are subbed into group.'''
        def tempfunc():
            return self.agrouptest.tr1 % {'td1':'Content Goes Here',
                'td2':'Test Page', 'td3':'Too many'}
        self.assertRaises(TypeError, tempfunc)            

    def test_lroot_dict_mod_toofew(self):
        '''Raises TypeError if too few items in dict are subbed into root.'''
        def tempfunc(): return self.gentemplate % {'content':'Content'}
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_dict_mod_toofew(self):
        '''Raises TypeError if too few items in dict are subbed into group.'''
        def tempfunc(): return self.gentemplate % {'content':'Content'}
        self.assertRaises(TypeError, tempfunc)

    def test_lroot_imod_mass_temp_subs(self):
        '''Tests a mass templates/substitution assignment on a root.'''
        final = '''<rss version="2.0">
<channel>
<title>Example</title>
<link>http://www.example.org/</link>
<description>RSS Example</description>
<language>en-us</language>
<pubDate id="cpubdate">$month $day, $year</pubDate>
<lastBuildDate id="lastbuilddate">%(month)s %(day)s, %(year)s</lastBuildDate>
<item class="item">
<title id="title">Example Title: First Example</title>
<link id="link">http://www.example.com/rss/5423092</link>
<guid id="guid" isPermaLink="true">http://www.example.com/rss/5423092</guid>
<description id="description">Example of assigning text to a field.</description>
<pubDate id="ipubdate">June 06, 2006</pubDate>
</item>
<item class="item">
<title id="title">Example Title: Second Example</title>
<link id="link">http://www.example.com/rss/5423093</link>
<guid id="guid" isPermaLink="true">http://www.example.com/rss/5423093</guid>
<description id="description">Example of group repetition.</description>
<pubDate id="ipubdate">June 06, 2006</pubDate>
</item>
</channel>
</rss>'''
        self.rss.item %= {
            'templates':{
                'title':{'text':'Example Title: $content'},
                'ipubdate':{'text':'$month $day, $year'},
                'link':{'text':'http://www.example.com/rss/$id'}},
            'subs':(
                ({'text':{'content':'First Example'}},
                {'text':{'id':'5423092'}},
                'http://www.example.com/rss/5423092',
                'Example of assigning text to a field.',
                {'text':{'month':'June', 'day':'06', 'year':'2006'}}),
                ({'text':{'content':'Second Example'}},
                {'text':{'id':'5423093'}},
                'http://www.example.com/rss/5423093',
                'Example of group repetition.',
                {'text':{'month':'June', 'day':'06', 'year':'2006'}}))}
        self.assertEqual(final, self.rss.pipe())

    def test_lroot_imod_extended_format(self):
        '''Tests an extended format substitution on a root.'''
        final = '<body><a id="fieldtest" href="caliban.html#test" title="This '\
        'link goes to test">This template is a first test.</a><a '\
        'id="fieldtest" href="caliban.html#linktest" title="This link goes to '\
        'Link Test">This other template is a link test.</a><tr '\
        'class="grouptest"><td id="groupfield1" align="left" title="This '\
        'column is column first">This first test is the first column.</td>'\
        '<td id="groupfield1" align="right" title="This col is column '\
        'second">This second test is the second column.</td><td '\
        'id="groupfield2" align="left" title="This test is next.">This test '\
        'is first.</td><td id="groupfield2">This coltest is a next.</td></tr></body>'
        self.subcombotest %= {
            'grouptest':{
                'groupfield1':{
                    'template':{
                        'text':'This %(one)s is the %(num)s column.',
                        'attrib':{'title':'This %(one)s is column %(num)s'}
                    }, 'sub':({
                        'text':{'one':'first test', 'num':'first'},
                        'attrib':{
                            'align':'left',
                            'title':{'one':'column', 'num':'first'}}}, {
                        'text':'This second test is the second column.',
                        'attrib':{
                            'align':'right',
                            'title':{'one':'col', 'num':'second'}}})},
                    'groupfield2':{
                        'template':{
                            'text':'This $test is a $fill.',
                            'attrib':{
                                'title':'This %(one)s is next.'}},
                        'sub':({
                            'text':'This test is first.',
                            'attrib':{
                                'align':'left',
                                'title':{'one':'test'}}}, {
                            'text':{'test':'coltest', 'fill':'next'},
                            'attrib':{                                    
                                 'href':{'link':'linktest'},
                                 'title':{'other':'Link Test'}}})}},
            'fieldtest':{
                'template':{
                    'text':'This %(run)s is a %(test)s.',
                    'attrib':{
                        'href':'caliban.html#%(link)s',
                        'title':'This link goes to %(other)s'}},
                'sub':({
                    'text':{'test':'first test', 'run':'template'},
                    'attrib':{
                        'href':{'link':'test'},
                        'title':{'other':'test'}}}, {
                    'text':{'test':'link test', 'run':'other template'},
                    'attrib':{
                         'href':{'link':'linktest'},
                         'title':{'other':'Link Test'}}})}}
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lfield_imod_extended_format(self):
        '''Tests an extended format substitution on a field.'''
        final = '<body><a id="fieldtest" href="caliban.html#test" ' \
            'title="This link goes to test">This template is a first ' \
            'test.</a><a id="fieldtest" href="caliban.html#linktest" ' \
            'title="This link goes to Link Test">This other template ' \
            'is a link test.</a><tr class="grouptest"><td ' \
            'id="groupfield1"/><td id="groupfield2"/></tr></body>'
        self.subcombotest.fieldtest %= {               
            'template':{
                'text':'This %(run)s is a %(test)s.',
                'attrib':{
                    'href':'caliban.html#%(link)s',
                    'title':'This link goes to %(other)s'}},
            'sub':({
                'text':{'test':'first test', 'run':'template'},
                'attrib':{
                    'href':{'link':'test'},
                    'title':{'other':'test'}}}, {
                'text':{'test':'link test', 'run':'other template'},
                'attrib':{
                     'href':{'link':'linktest'},
                     'title':{'other':'Link Test'}}})}
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lfield_imod_attrib_extended_format(self):
        '''Tests an extended attribute format substitution on a field.'''
        final = '<body><a id="fieldtest" href="caliban.html#test" title="This '\
        'link goes to test">This is a test.</a><a id="fieldtest" '\
        'href="caliban.html#linktest" title="This link goes to Link Test">This is another test.'\
        '</a><tr class="grouptest"><td id="groupfield1"/><td id="groupfield2"/></tr></body>'
        self.subcombotest.fieldtest %= {               
            'template':{
                'attrib':{
                    'href':'caliban.html#%(link)s',
                    'title':'This link goes to %(other)s'}},
            'sub':({
                'text':'This is a test.',
                'attrib':{
                    'href':{'link':'test'},
                    'title':{'other':'test'}}}, {
                'text':'This is another test.',
                'attrib':{
                     'href':{'link':'linktest'},
                     'title':{'other':'Link Test'}}})}
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lfield_imod_text_extended_format(self):
        '''Tests a text extended format substitution on a field.'''
        final = '<body><a id="fieldtest" href="atest">This template is ' \
            'a first test.</a><a id="fieldtest" href="atest">This other' \
            ' template is a link test.</a><tr class="grouptest"><td id' \
            '="groupfield1"/><td id="groupfield2"/></tr></body>'
        self.subcombotest.fieldtest %= {               
            'template':{
                'text':'This %(run)s is a %(test)s.'},
            'sub':({
                'text':{'test':'first test', 'run':'template'}}, {
                'text':{'test':'link test', 'run':'other template'}})}
        self.assertEqual(final, self.subcombotest.pipe())            

    def test_lgroup_imod_combo_extended_format(self):
        '''Tests an extended format substitution on a group.'''
        final = '<body><a id="fieldtest" href="atest"/><tr class="grouptest">'\
        '<td id="groupfield1" align="left" title="This column is column first">'\
        'This first test is the first column.</td><td id="groupfield1" '\
        'align="right" title="This col is column second">This second test is '\
        'the second column.</td><td id="groupfield2" align="left" title="This '\
        'test is next.">This test is first.</td><td id="groupfield2">This '\
        'coltest is a next.</td></tr></body>'
        self.subcombotest.grouptest %= {
                'groupfield1':{
                    'template':{
                        'text':'This %(one)s is the %(num)s column.',
                        'attrib':{'title':'This %(one)s is column %(num)s'}
                     },'sub':({
                        'text':{'one':'first test', 'num':'first'},
                        'attrib':{
                            'align':'left',
                            'title':{'one':'column', 'num':'first'}}}, {
                        'text':'This second test is the second column.',
                        'attrib':{
                            'align':'right',
                            'title':{'one':'col', 'num':'second'}}})},
                    'groupfield2':{
                        'template':{
                            'text':'This $test is a $fill.',
                            'attrib':{
                                'title':'This %(one)s is next.'}},
                        'sub':({
                            'text':'This test is first.',
                            'attrib':{
                                'align':'left',
                                'title':{'one':'test'}}}, {
                            'text':{'test':'coltest', 'fill':'next'},
                            'attrib':{                                    
                                 'href':{'link':'linktest'},
                                 'title':{'other':'Link Test'}}})}}
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lfield_pow(self):
        '''Tests a expansion of a field.'''
        atst = self.powtemplate.content ** self.powtup
        self.assertEqual(self.powtest1, atst.render())

    def test_lfield_ipow(self):
        '''Tests a modifying expansion of a field.'''
        self.powtemplate.content **= self.powtup
        self.assertEqual(self.powtest1, self.powtemplate.content.pipe())

    def test_lgroup_ipow(self):
        '''Tests a modifying expansion of a group.'''
        self.agrouptest.tr1 **= self.grouptup
        self.assertEqual(self.groupow, self.agrouptest.tr1.pipe())

    def test_lfield_pow_rep(self):
        '''Raises TypeError if field expansion exceeds max repetitions.'''
        def tempfunc():
            atst = self.powtemplate.default
            atst.content.max = 1
            atst.content ** self.powtup
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_pow_rep(self):
        '''Raises TypeError if group expansion exceeds max repetitions.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.max = 1
            return atst.tr1 ** self.grouptup
        self.assertRaises(TypeError, tempfunc)                       

    def test_lfield_pow_wrongtype(self):
        '''Raises TypeError if wrong type passed in for field expansion.'''
        def tempfunc(): return self.powtemplate ** 'This is a test.'
        self.assertRaises(TypeError, tempfunc)

    def test_lgroup_pow_wrongtype(self):
        '''Raises TypeError if wrong type passed in for group expansion.'''
        def tempfunc(): return self.agrouptest.tr1 ** 'This is a test.'
        self.assertRaises(TypeError, tempfunc)            

    def test_lfield_delattr_dict(self):
        '''Tests deletion of field attributes from internal dict.'''
        atst = self.btemplate.default
        del atst.content
        self.assertEqual(False, atst._fielddict.has_key('content'))

    def test_lgroup_delattr_dict(self):
        '''Tests deletion of group attributes from internal dict.'''
        atst = self.agrouptest.default
        del atst.tr1
        self.assertEqual(False, atst._fielddict.has_key('tr1'))

    def test_lsubfield_delattr_dict(self):
        '''Tests deletion of group attributes from internal dict.'''
        atst = self.agrouptest.default
        del atst.tr1.td1
        self.assertEqual(False, atst.tr1._fielddict.has_key('td1'))

    def test_lfield_delattr(self):
        '''Tests deletion of field attributes from internal list.'''
        atst = self.btemplate.default
        del atst.content
        self.assertEqual(False, 'content' in atst)

    def test_lgroup_delattr(self):
        '''Tests deletion of group attributes from internal list.'''
        atst = self.agrouptest.default
        del atst.tr1
        self.assertEqual(False, 'tr1' in atst)

    def test_lsubfield_delattr(self):
        '''Tests deletion of subfield attributes from internal list.'''
        atst = self.agrouptest.default
        del atst.tr1.td1
        self.assertEqual(False, 'td1' in atst.tr1)

    def test_lattribute_get(self):
        '''Tests accessing XML attribute attributes.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        self.assertEqual(atst.tr1.td1.align, 'left')
        
    def test_lattribute_set(self):
        '''Tests setting XML attribute attributes.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        atst.tr1.td1.align = 'right'
        self.assertEqual(atst.tr1.td1.align, 'right')

    def test_lattribute_set_dict(self):
        '''Tests setting XML attribute attributes with a dict.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        atst.tr1.td1.atemplates({'align':'This is $dir'})
        atst.tr1.td1.align = {'dir':'right'}
        self.assertEqual(atst.tr1.td1.align, 'This is right')

    def test_lfield_delete_attribute(self):
        '''Tests deletion of XML attribute attributes.'''
        atst = Template('<html><body><p align="left" id="content"></p>' \
            '</body></html>', engine='lxml')
        del atst.content.align
        self.assertEqual(False, hasattr(atst.content, 'align'))

    def test_lsubfield_delete_attribute(self):
        '''Tests deletion of subfield XML attribute attributes.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        del atst.tr1.td1.align
        self.assertEqual(False, hasattr(atst.tr1.td1, 'align'))           

    def test_lattribute_get_key_noauto(self):
        '''Tests getting XML attributes via key w/o automagic.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        self.assertEqual(atst['tr1']['td1']['align'], 'left')

    def test_lattribute_set_key_noauto(self):
        '''Tests setting attributes via key w/o automagic.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', False, engine='lxml')
        atst['tr1']['td1']['align'] = 'right'
        self.assertEqual(atst['tr1']['td1']['align'], 'right')

    def test_lattribute_set_key_noauto_dict(self):
        '''Tests setting attributes via key w/o automagic with a dict.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', False, engine='lxml')
        atst['tr1']['td1'].atemplates({'align':'This is $dir'})
        atst['tr1']['td1']['align'] = {'dir':'right'}
        self.assertEqual(atst['tr1']['td1']['align'], 'This is right')

    def test_lfield_attribute_delete_key_noauto(self):
        '''Tests deletion of field XML attributes via key w/o automagic.'''
        atst = Template('<html><body><p align="left" id="content"></p>' \
            '</body></html>', False, engine='lxml')
        del atst['content']['align']
        self.assertEqual(False, 'align' in atst['content'])

    def test_lsubfield_attribute_delete_key_noauto(self):
        '''Tests deletion of subfield XML attributes via key on automagic.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', False, engine='lxml')
        del atst['tr1']['td1']['align']
        self.assertEqual(False, 'align' in atst['tr1']['td1'])

    def test_lattribute_get_key(self):
        '''Tests getting XML attributes via key.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        self.assertEqual(atst.tr1.td1['align'], 'left')

    def test_lattribute_set_key(self):
        '''Tests setting XML attributes via key.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        atst.tr1.td1['align'] = 'right'
        self.assertEqual(atst.tr1.td1['align'], 'right')
        
    def test_lattribute_set_key_dict(self):
        '''Tests setting attributes via key with a dict.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        atst.tr1.td1.atemplates({'align':'This is $dir'})
        atst.tr1.td1['align'] = {'dir':'right'}
        self.assertEqual(atst.tr1.td1['align'], 'This is right')

    def test_lfield_attribute_delete_key(self):
        '''Tests deletion of field XML attributes via key.'''
        atst = Template('<html><body><p align="left" id="content"></p>' \
            '</body></html>', engine='lxml')
        del atst.content['align']
        self.assertEqual(False, hasattr(atst.content, 'align'))

    def test_lsubfield_attribute_delete_key(self):
        '''Tests deletion of subfield XML attributes via key.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
        'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        del atst.tr1.td1['align']
        self.assertEqual(False, hasattr(atst.tr1.td1, 'align'))        

    def test_lattribute_len(self):
        '''Tests discovering the number of XML attributes in a field.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
            'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        self.assertEqual(len(atst.tr1.td1), 2)

    def test_lattribute_iter(self):
        '''Tests accessing XML attributes via iterator.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
            'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        test = [i for i in atst.tr1.td1]
        self.assertEqual(['id', 'align'], test)

    def test_lattribute_contains(self):
        '''Tests if an attribute is in a field or not.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
            'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        self.assertEqual(True, 'align' in atst.tr1.td1)

    def test_lattribute_contains_not(self):
        '''Tests if an attribute is in a field or not.'''
        atst = Template('<table><tr class="tr1"><td id="td1" ' \
            'align="left"/><td id="td2"/></tr></table>', engine='lxml')
        self.assertEqual(False, 'align' in atst.tr1)         

    def test_lupdate(self):
        '''Tests mass addition of XML attributes.'''
        final = '<head><link id="test" href="thing.css" type="text/css"/></head>'
        test = Template('<head><link id="test"/></head>', engine='lxml')
        test.test.update({'href':'thing.css', 'type':'text/css'})
        self.assertEqual(final, test.render())

    def test_lupdate_wrong_type(self):
        '''Tests update to see if it throws exception with wrong type.'''
        def tempfunc():
            '''Stub'''
            test = Template('<head><link id="test"/></head>', engine='lxml')
            test.test.update(tuple())
        self.assertRaises(TypeError, tempfunc)

    def test_lfield_purge(self):
        '''Tests if an XML attribute is purged from a field or not.'''
        final = '<body><a/><tr class="grouptest"><td id="groupfield1"/>' \
             '<td id="groupfield2"/></tr></body>'
        self.subcombotest.fieldtest.purge('href', 'id')
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lsubfield_purge(self):
        '''Tests if an XML attribute is purged from a field or not.'''
        final = '<body><a id="fieldtest" href="atest"/>' \
             '<tr class="grouptest"><td/><td id="groupfield2"/></tr></body>'
        self.subcombotest.grouptest.groupfield1.purge('id')
        self.assertEqual(final, self.subcombotest.pipe())          

    def test_lroot_nomarks(self):
        '''Tests deletion of marks and groupmarks of a root's children.'''
        final = '<body><a href="atest"/><tr><td/><td/></tr></body>'
        del self.subcombotest.mark
        del self.subcombotest.groupmark
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lgroup_nomarks(self):
        '''Tests deletion of marks and groupmarks of a field's children.'''
        final = '<body><a id="fieldtest" href="atest"/><tr><td/><td/>' \
            '</tr></body>'
        del self.subcombotest.grouptest.mark
        del self.subcombotest.grouptest.groupmark
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lfield_nomarks(self):
        '''Tests deletion of marks of a field.'''
        final = '<body><a href="atest"/><tr class="grouptest">' \
        '<td id="groupfield1"/><td id="groupfield2"/></tr></body>'
        del self.subcombotest.fieldtest.mark
        self.assertEqual(final, self.subcombotest.pipe())

    def test_lsubfield_nomarks(self):
        '''Tests deletion of marks of a subfield.'''
        final = '<body><a id="fieldtest" href="atest"/>' \
            '<tr class="grouptest"><td/><td id="groupfield2"/></tr></body>'
        del self.subcombotest.grouptest.groupfield1.mark
        self.assertEqual(final, self.subcombotest.pipe())

    def test_latemplate_interpolation(self):
        '''Tests substituting attributes text with string interpolation.'''
        atst = self.gentemplate.default
        atst.content.atemplates({'span':'%(direction)s'})
        atst.content.update({'span':{'direction':'left'}})
        self.assertEqual(atst.content.render(), '<p id="content" span="left"/>')         

    def test_latemplate_string_template(self):
        '''Tests substituting attributes text with string.Template.'''
        atst = self.gentemplate.default
        atst.content.atemplates({'span':'$direction'})
        atst.content.update({'span':{'direction':'left'}})
        self.assertEqual(atst.content.render(),
            '<p id="content" span="left"/>')

    def test_latemplate_source_interpolation(self):
        '''Tests getting attribute template from inline text in the source.'''
        final = '<body><p id="content" title="This run is a test."/></body>'
        atst = Template('<body><p id="content" title="This %(t1)s is a ' \
            '%(t2)s"/></body>', engine='lxml')
        atst.content.update({'title':{'t1':'run', 't2':'test.'}})
        self.assertEqual(final, atst.render())         

    def test_latemplate_source_string_template(self):
        '''Tests getting attribute template from inline text in the source.'''
        final = '<body><p id="content" title="This run is a test."/></body>'
        atst = Template('<body><p id="content" title="This $t1 is a ' \
            '$t2"/></body>', engine='lxml')
        atst.content.update({'title':{'t1':'run', 't2':'test.'}})
        self.assertEqual(final, atst.render())        

    def test_latemplate_wrongtype(self):
        '''Tests substituting inline attribute text.'''
        def tempfunc():
            atst = self.gentemplate.default
            atst.content.atemplates('span')
        self.assertRaises(TypeError, tempfunc)

    def test_latemplate_nodelimiter(self):
        '''Tests substituting inline attribute text.'''
        def tempfunc():
            atst = self.gentemplate.default
            atst.content.atemplates({'span':'direction'})
        self.assertRaises(TypeError, tempfunc)        

    def test_lauto_auto_off_attribute(self):
        '''Tests if auto turns off magical attributes for attributes.'''
        atst = Template('<html><head><title id="title" style="style"/>' \
            '</head><body><p id="content"/></body></html>', False, engine='lxml')
        self.assertEqual(hasattr(atst[0], 'style'), False)        

    def test_lfield_getitem(self):
        '''Tests getting field contents by index.'''
        atst = self.btemplate.default
        atst.content %= 'Test'
        self.assertEqual('Test', atst[0].text)

    def test_lgroup_getitem(self):
        '''Tests getting group contents by index.'''
        atst = self.agrouptest.default
        self.assertEqual(True, hasattr(atst[0], 'td1'))

    def test_lsubfield_getitem(self):
        '''Tests getting subfield contents by index.'''
        atst = self.agrouptest.default
        atst.tr1.td1 %= 'Test'
        self.assertEqual('Test', atst[0][0].text)

    def test_lfield_setitem(self):
        '''Tests setting field contents by index.'''
        atst = self.btemplate.default
        atst[0] %= 'Test'
        self.assertEqual('Test', atst[0].text)

    def test_lgroup_setitem(self):
        '''Tests setting group contents by index.'''
        atst = self.agrouptest.default
        atst[0].id = 'Test'
        self.assertEqual('Test', atst[0].id)

    def test_lsubfield_setitem(self):
        '''Tests setting subfield contents by index.'''
        atst = self.agrouptest.default
        atst[0][0] %= 'Test'
        self.assertEqual('Test', atst[0][0].text)
        
    def test_lfield_delitem(self):
        '''Tests deleting fields by index.'''
        atst = self.btemplate.default
        del atst[0]
        self.assertEqual(False, hasattr(atst, 'content'))

    def test_lgroup_delitem(self):
        '''Tests deleting groups by index.'''
        atst = self.agrouptest.default
        del atst[0]
        self.assertEqual(False, hasattr(atst, 'tr1'))

    def test_lsubfield_delitem(self):
        '''Tests deleting subfields by index.'''
        atst = self.agrouptest.default
        del atst[0][0]
        self.assertEqual(False, hasattr(atst.tr1, 'td1'))

    def test_lfield_getitem_key(self):
        '''Tests getting field contents by key.'''
        atst = self.btemplate.default
        atst.content %= 'Test'
        self.assertEqual('Test', atst['content'].text)

    def test_lgroup_getitem_key(self):
        '''Tests getting group contents by key.'''
        atst = self.agrouptest.default
        self.assertEqual(True, hasattr(atst['tr1'], 'td1'))

    def test_lsubfield_getitem_key(self):
        '''Tests getting subfield contents by key.'''
        atst = self.agrouptest.default
        atst.tr1.td1 %= 'Test'
        self.assertEqual('Test', atst['tr1']['td1'].text)

    def test_lfield_setitem_key(self):
        '''Tests setting field contents by key.'''
        atst = self.btemplate.default
        atst['content'] %= 'Test'
        self.assertEqual('Test', atst['content'].text)

    def test_lgroup_setitem_key(self):
        '''Tests setting group contents by key.'''
        atst = self.agrouptest.default
        atst['tr1'].id = 'Test'
        self.assertEqual('Test', atst['tr1'].id)

    def test_lsubfield_setitem_key(self):
        '''Tests setting subfield contents by key.'''
        atst = self.agrouptest.default
        atst['tr1']['td1'] %= 'Test'
        self.assertEqual('Test', atst['tr1']['td1'].text)
        
    def test_lfield_delitem_key(self):
        '''Tests deleting fields by key.'''
        atst = self.btemplate.default
        del atst['content']
        self.assertEqual(False, hasattr(atst, 'content'))

    def test_lgroup_delitem_key(self):
        '''Tests deleting groups by key.'''
        atst = self.agrouptest.default
        del atst['tr1']
        self.assertEqual(False, hasattr(atst, 'tr1'))

    def test_lgroup_field_delitem_key(self):
        '''Tests deleting subfield by key.'''
        atst = self.agrouptest.default
        del atst['tr1']['td1']
        self.assertEqual(False, hasattr(atst.tr1, 'td1'))        

    def test_lroot_len(self):
        '''Tests getting number of fields in a root Template.'''
        atst = self.btemplate.default
        self.assertEqual(1, len(atst))

    def test_lgroup_len(self):
        '''Tests getting number of fields in a group.'''
        atst = self.agrouptest.default
        self.assertEqual(2, len(atst.tr1))

    def test_lcontains_true(self):
        '''Tests if a field of a certain name is in a root Template.'''
        atst = self.btemplate.default
        val = 'content' in atst
        self.assertEqual(True, val)

    def test_lcontains_false(self):
        '''Tests if a field of a certain name is not in a root Template.'''
        atst = self.btemplate.default
        val = 'content1' in atst
        self.assertEqual(False, val)

    def test_liter_false(self):
        '''Tests if an iterator finds false values.'''
        atst = self.btemplate.default
        val = False
        for i in atst:
            if i['id'] == 'content1': val = True
        self.assertEqual(False, val)

    def test_liter_true(self):
        '''Tests if an iterator finds true values.'''
        atst = self.btemplate.default
        val = False
        for i in atst:
            if i['id'] == 'content': val = True
        self.assertEqual(True, val)

    def test_liter_assign(self):
        '''Tests if an iterator assigns correctly.'''
        atst = self.btemplate.default
        for i in atst: i %= 'Test'
        self.assertEqual('Test', atst.content.text)

    def test_ltemplates(self):
        '''Tests batch addition of templates to a root Template.'''
        final = '<body><a id="fieldtest" href="caliban.html#test" '\
        'title="This link goes to test">This template is a first test.</a><a '\
        'id="fieldtest" href="caliban.html#linktest" title="This link goes to '\
        'Link Test">This other template is a link test.</a><tr '\
        'class="grouptest"><td id="groupfield1" align="left" title="This '\
        'column is column first">This first test is the first column.</td>' \
        '<td id="groupfield1" align="right" title="This col is column '\
        'second">This second test is the second column.</td><td '\
        'id="groupfield2" align="left" title="This test is next.">This test '\
        'is first.</td><td id="groupfield2">This coltest is a next.</td></tr></body>'
        self.subcombotest.templates({
            'grouptest':{
                'groupfield1':{
                    'text':'This %(one)s is the %(num)s column.',
                    'attrib':{'title':'This %(one)s is column %(num)s'}},
                'groupfield2':{
                    'text':'This $test is a $fill.',
                    'attrib':{
                        'title':'This %(one)s is next.'}}},                
            'fieldtest':{
                'text':'This %(run)s is a %(test)s.',
                'attrib':{
                    'href':'caliban.html#%(link)s',
                    'title':'This link goes to %(other)s'}}})
        self.subcombotest %= {
            'grouptest':{
                'groupfield1':{                        
                    'sub':({
                        'text':{'one':'first test', 'num':'first'},
                        'attrib':{
                            'align':'left',
                            'title':{'one':'column', 'num':'first'}}}, {
                        'text':'This second test is the second column.',
                        'attrib':{
                            'align':'right',
                            'title':{'one':'col', 'num':'second'}}})},
                    'groupfield2':{
                        'sub':({
                            'text':'This test is first.',
                            'attrib':{
                                'align':'left',
                                'title':{'one':'test'}}}, {
                            'text':{'test':'coltest', 'fill':'next'},
                            'attrib':{                                    
                                 'href':{'link':'linktest'},
                                 'title':{'other':'Link Test'}}})}},
            'fieldtest':{
                'sub':({
                    'text':{'test':'first test', 'run':'template'},
                    'attrib':{
                        'href':{'link':'test'},
                        'title':{'other':'test'}}}, {
                    'text':{'test':'link test', 'run':'other template'},
                    'attrib':{
                         'href':{'link':'linktest'},
                         'title':{'other':'Link Test'}}})}}
        self.assertEqual(final, self.subcombotest.pipe())

    def test_ltemplates_mixin(self):
        '''Tests batch addition of templates to a root Template.'''
        final = '<body><a id="fieldtest" href="atest"/><tr class="grouptest">'\
        '<td id="groupfield1" align="left" title="This column is column '\
        'first">one</td><td id="groupfield1" align="right" title="This col '\
        'is column second">This second test is the second column.</td><td '\
        'id="groupfield2">This test is first.</td><td id="groupfield2">This '\
        'coltest is a next.</td></tr></body>'
        self.subcombotest.grouptest.templates({
            'groupfield1':{
                'attrib':{'title':'This %(one)s is column %(num)s'}},
            'groupfield2':{
                'text':'This $test is a $fill.'}})
        self.subcombotest.grouptest %= {
                'groupfield1':{
                    'sub':({
                        'text':'one',
                        'attrib':{
                            'align':'left',
                            'title':{'one':'column', 'num':'first'}}}, {
                        'text':'This second test is the second column.',
                        'attrib':{
                            'align':'right',
                            'title':{'one':'col', 'num':'second'}}})},
                'groupfield2':{
                    'sub':({
                        'text':'This test is first.'}, {
                        'text':{'test':'coltest', 'fill':'next'}})}}
        self.assertEqual(final, self.subcombotest.pipe())

    def test_ltemplates_toomany(self):
        '''Raises TypeError if too many templates.'''
        def tempfunc():
            '''Stub'''
            self.subcombotest.grouptest.templates({
                'groupfield1':{
                    'attrib':{'title':'This %(one)s is column %(num)s'}},
                'groupfield2':{
                    'text':'This $test is a $fill.'},
                'groupfield3':{
                    'text':'This $test is a $fill.'}})
        self.assertRaises(TypeError, tempfunc)

    def test_ltemplates_wrongtype(self):
        '''Raises TypeError if wrong type passed to templates.'''
        def tempfunc():
            '''Stub'''
            self.subcombotest.grouptest.templates([
                {'title':'This %(one)s is column %(num)s'},
                {'text':'This $test is a $fill.'},
                {'text':'This $test is a $fill.'}])
        self.assertRaises(TypeError, tempfunc)        
        
    def test_ltext_get(self):
        '''Tests if text properties are set and fetched correctly.'''
        atst = self.btemplate.default
        atst.content.text = 'Test'
        self.assertEqual('Test', atst.content.text)

    def test_ltext_delete(self):
        '''Tests if text values are deleted correctly.'''
        atst = self.btemplate.default
        atst.content.text = 'Test'
        del atst.content.text
        self.assertEqual(None, atst.content.text)        

    def test_ltext_wrongtype(self):
        '''Raises a TypeError if wrong type passed to text.'''
        def tempfunc(): self.gentemplate.content.text = [{'place':'test'}]
        self.assertRaises(TypeError, tempfunc)

    def test_ltemplate_from_src_string_template(self):
        '''Tests a template passed in with markup with the Template source.'''
        final = '<body><p id="stuff">This run is a test.</p></body>'
        ast = Template('<body><p id="stuff">This $tst1 is a $tst2</p></body>', engine='lxml')
        ast.stuff.text = {'tst1':'run', 'tst2':'test.'}
        self.assertEqual(final, ast.render())

    def test_ltemplate_from_src_interpolation(self):
        '''Tests a template passed in with markup with the Template source.'''
        final = '<body><p id="stuff">This run is a test.</p></body>'
        ast = Template('<body><p id="stuff">This %(tst1)s is a %(tst2)s' \
            '</p></body>', engine='lxml')
        ast.stuff.text = {'tst1':'run', 'tst2':'test.'}
        self.assertEqual(final, ast.render())         

    def test_ltemplate_nodelimiter(self):
        '''Tests setting an inline template with no delimiter'''
        def tempfunc(): self.gentemplate.content.template = 'This is a place'
        self.assertRaises(TypeError, tempfunc)

    def test_ltemplate_wrongtype(self):
        '''Tests setting an inline template with the wrong type'''
        def tempfunc(): self.gentemplate.content.template = ['This is a place']
        self.assertRaises(TypeError, tempfunc)              

    def test_ltemplate_text_interpolation(self):
        '''Tests setting inline text with a string interpolation template.'''
        final = '<p id="content">This is a test</p>'
        atst = self.gentemplate.default
        atst.content.template = 'This is a %(place)s'
        atst.content.text = {'place':'test'}
        self.assertEqual(atst.content.render(), final)            
        
    def test_ltemplate_text_string_template(self):
        '''Tests setting inline text with a string.Template template.'''
        final = '<p id="content">This is a test</p>'
        atst = self.gentemplate.default
        atst.content.template = 'This is a $place'
        atst.content.text = {'place':'test'}
        self.assertEqual(atst.content.render(), final)               

    def test_lroot_max(self):
        '''Tests max assignment on a root.'''
        atst = self.gentemplate.default
        atst.max = 100
        self.assertEqual(200, atst.title.max + atst.content.max)

    def test_lgroup_max(self):
        '''Tests max assignment on a group.'''
        atst = self.agrouptest.default
        atst.max = 100
        self.assertEqual(200, atst.tr1.td1.max + atst.tr1.td2.max)           

    def test_lauto_auto_off_hasattr(self):
        '''Tests if auto turns off magical attributes for elements.'''
        atst = Template('<html><head><title id="title"/></head><body>' \
            '<p id="content"/></body></html>', False, engine='lxml')
        self.assertEqual(hasattr(atst, 'title'), False)    

    def test_lroot_append(self):
        '''Tests appending a field to a root Template.'''
        final = '<html><head><title id="title"/></head>' \
            '<title id="title"/></html>'
        self.atemplate.append(self.atemplate.title.default)
        self.assertEqual(final, self.atemplate.pipe())

    def test_lroot_append_element(self):
        '''Tests appending an element to a root Template.'''
        final = '<html><head><title id="title"/></head>' \
            '<p/></html>'
        self.atemplate.append(_Element('p'))
        self.assertEqual(final, self.atemplate.pipe())            

    def test_lfield_append(self):
        '''Tests appending a root Template to a field.'''
        final = '<html><head><title id="title"><html><head>' \
            '<title id="title"/></head></html></title></head></html>'      
        self.atemplate.title.append(self.atemplate.default)
        self.assertEqual(final, self.atemplate.pipe())

    def test_lfield_append_element(self):
        '''Tests appending an element to a field.'''
        final = '<html><head><title id="title"><p/></title></head>' \
            '</html>'      
        self.atemplate.title.append(_Element('p'))
        self.assertEqual(final, self.atemplate.pipe())            

    def test_lgroup_append(self):
        '''Tests appending a root Template to a group.'''
        final = '<table><tr class="tr1"><td id="td1"/><td id="td2"/>' \
            '<table><tr class="tr1"><td id="td1"/><td id="td2"/></tr>' \
            '</table></tr></table>'  
        self.agrouptest.tr1.append(self.agrouptest.default)
        self.assertEqual(final, self.agrouptest.pipe())

    def test_lgroup_append_reset_test(self):
        '''Tests appending a root Template to a group and reseting.'''
        final = '<table><tr class="tr1"><td id="td1"/><td id="td2"/>' \
            '<table><tr class="tr1"><td id="td1"/><td id="td2"/></tr>' \
            '</table></tr></table>'   
        self.agrouptest.tr1.append(self.agrouptest.default)
        test = self.agrouptest.render()
        self.agrouptest.tr1.reset()
        self.assertEqual(final, test)            

    def test_lgroup_append_element(self):
        '''Tests appending an element to a group.'''
        final = '<table><tr class="tr1"><td id="td1"/><td id="td2"/>' \
            '<p/></tr></table>'  
        self.agrouptest.tr1.append(_Element('p'))
        self.assertEqual(final, self.agrouptest.pipe())

    def test_lroot_append_wrongtype(self):
        '''Raises TypeError if appending a wrong type to a root Template.'''
        def tempfunc(): self.atemplate.append('p')
        self.assertRaises(TypeError, tempfunc)            

    def test_lgroup_append_wrongtype(self):
        '''Raises TypeError if appending a wrong type to a group.'''
        def tempfunc(): self.agrouptest.tr1.append('p')
        self.assertRaises(TypeError, tempfunc)            

    def test_lfield_append_wrongtype(self):
        '''Raises TypeError if appending the wrong type to a field.'''
        def tempfunc(): self.atemplate.title.append('p')
        self.assertRaises(TypeError, tempfunc) 

    def test_lexclude(self):
        '''Tests exclusion on a root Template.'''
        a = Template(engine='lxml')
        a.exclude('td1', 'td2')
        a.fromstring('<tr><td id="td1"/><td id="td2"/><td id="td3"/></tr>')
        self.assertEqual(True, len(a) == 1)            

    def test_lexclude_live(self):
        '''Tests exclusion on a live root Template.'''
        testfilter = Template('<table><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr><p id="r"/></table>', engine='lxml')
        testfilter.exclude('tr1', 'r')
        self.assertEqual(True, len(testfilter) == 0)

    def test_lexclude_group(self):
        '''Tests exclusion on a group.'''
        a = Template(engine='lxml')
        a.exclude('td1', 'td2')
        a.fromstring('<table><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr><p id="r"/></table>')
        self.assertEqual(True, len(a) == 1)            

    def test_lexclude_live_group(self):
        '''Tests exclusion on a live group.'''
        testfilter = Template('<table><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr><p id="r"/></table>', engine='lxml')
        testfilter.exclude('td1', 'td2')
        self.assertEqual(True, len(testfilter) == 1)        

    def test_lexclude_wrongtype(self):
        '''Raises TypeError if wrong type included.'''
        def tempfunc(): self.agrouptest.exclude(['eeee'])
        self.assertRaises(AttributeError, tempfunc)             

    def test_lroot_include(self):
        '''Tests inclusion on a Template.'''
        testfilter = Template(engine='lxml')
        testfilter.exclude('td1')
        testfilter.fromstring('<tr><td id="td1"/><td id="td2"/></tr>')
        testfilter.include('td1')
        self.assertEqual(True, hasattr(testfilter, 'td1'))

    def test_linclude_live(self):
        '''Tests inclusion on a live Template.'''
        testfilter = Template('<table><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr><p id="r"/></table>', engine='lxml')
        testfilter.exclude('tr1', 'r')
        testfilter.include('tr1', 'r')
        self.assertEqual(True, len(testfilter) == 2)

    def test_linclude_group(self):
        '''Tests inclusion on a group.'''
        a = Template(engine='lxml')
        a.exclude('td1', 'td2')
        a.fromstring('<table><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr><p id="r"/></table>')
        a.include('td1', 'td2')
        self.assertEqual(True, len(a.tr1) == 2)            

    def test_linclude_live_group(self):
        '''Tests inclusion on a live group.'''
        testfilter = Template('<table><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr><p id="r"/></table>', engine='lxml')
        testfilter.exclude('td1', 'td2')
        testfilter.include('td1', 'td2')
        self.assertEqual(True, len(testfilter.tr1) == 2)         

    def test_linclude_wrongtype(self):
        '''Tests if inclusion raises an exception with wrong type passed.'''
        def tempfunc(): self.agrouptest.include(['eeee'])
        self.assertRaises(TypeError, tempfunc)              

    def test_lgroup_under_group_proc(self):
        '''Tests proper group within group processing.'''
        testfilter = Template('<div><table class="thing">' \
            '<th id="thing2"/><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr></table></div>', engine='lxml')
        self.assertEqual(False, hasattr(testfilter.thing, 'td1'))

    def test_lgroup_under_group_proc2(self):
        '''Tests proper group within group processing again.'''
        testfilter = Template('<div><table class="thing">' \
            '<th id="thing2"/><tr class="tr1"><td id="td1"/>' \
            '<td id="td2"/></tr></table></div>', engine='lxml')
        self.assertEqual(True, hasattr(testfilter.thing, 'thing2'))
        
    def test_lno_empty_group(self):
        '''Tests if empty groups are properly pruned.'''
        testfilter = Template(engine='lxml')
        testfilter.exclude('td1')
        testfilter.fromstring('<div><table class="thing"><tr class="tr1">' \
            '<td id="td1"/><td id="td2"/></tr></table></div>')
        testfilter.include('td1')
        self.assertEqual(False, hasattr(testfilter, 'thing'))          

    def test_lhtmltemplate_output_html4(self):
        '''Tests for correct HTML 4.0 output.'''
        final = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 '\
        'Transitional//EN">\n<html><head><link href="test.css" '\
        'type="text/css"><title id="title">Test Page</title>'\
        '</head><body><p id="content">Test Content</p></body></html>'
        self.htmlt %= ('Test Page', 'Test Content')
        self.assertEqual(final, self.htmlt.pipe())

    def test_lhtmltemplate_output_xhtml10(self):
        '''Tests for correct XHTML 1.0 output.'''
        final = '<?xml version="1.0" encoding="utf-8"?>\n<?xml-stylesheet '\
        'href="test.css" type="text/css" ?>\n<!DOCTYPE html PUBLIC '\
        '"-//W3C//DTD XHTML 1.0 Strict//EN" '\
        '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html>'\
        '<head><link href="test.css" type="text/css"/><title id="title">'\
        'Test Page</title></head><body><p id="content">Test Content</p></body></html>'
        self.htmlt %= ('Test Page', 'Test Content')
        self.assertEqual(final, self.htmlt.pipe(None, 'xhtml10'))

    def test_lhtmltemplate_output_xhtml11(self):
        '''Tests for correct XHTML 1.1 output.'''
        final = '<?xml version="1.0" encoding="utf-8"?>\n<?xml-stylesheet ' \
        'href="test.css" type="text/css" ?>\n<!DOCTYPE html PUBLIC '\
        '"-//W3C//DTD XHTML 1.1//EN" '\
        '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n<html><head><link '\
        'href="test.css" type="text/css"/><title id="title">Test Page</title>'\
        '</head><body><p id="content">Test Content</p></body></html>'
        self.htmlt %= ('Test Page', 'Test Content')
        self.assertEqual(final, self.htmlt.pipe(None, 'xhtml11'))

    def test_lwsgitemplate(self):
        '''Tests for correct XML output.'''
        final = ['<html><head/><body><p id="test">Hello world!\n</p></body>' \
            '</html>']
        source = '<html><head/><body><p id="test"/></body></html>'
        def simple_app(environ, start_response):
            start_response('200 OK', ('Content-type','text/html'))              
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGITemplate(simple_app, source, engine='lxml')
        self.assertEqual(app({}, fake_response), final)            
                
    def test_lwsgihtmltemplate(self):
        '''Tests for correct HTML 4.01 output.'''
        final = ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 ' \
            'Transitional//EN">\n<html><head><body><p id="test">' \
            'Hello world!\n</p></body></html>']
        source = '<html><head/><body><p id="test"/></body></html>'
        def simple_app(environ, start_response):
            start_response('200 OK', ('Content-type','text/html'))            
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGIHTMLTemplate(simple_app, source, engine='lxml')
        self.assertEqual(app({}, fake_response), final)

    def test_lwsgihtmltemplate_xhtml10(self):
        '''Tests for correct XHTML 1.0 output.'''
        final = ['<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html '\
            'PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '\
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html>' \
            '<head/><body><p id="test">Hello world!\n</p></body></html>']
        source = '<html><head/><body><p id="test"/></body></html>'
        def simple_app(environ, start_response):
            start_response('200 OK', ('Content-type','text/html'))             
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGIHTMLTemplate(simple_app, source, format='xhtml10', engine='lxml')
        self.assertEqual(app({}, fake_response), final)

    def test_lwsgihtmltemplate_xhtml11(self):
        '''Tests for correct XHTML 1.1 output.'''
        final = ['<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html ' \
            'PUBLIC "-//W3C//DTD XHTML 1.1//EN" ' \
            '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n<html>' \
            '<head/><body><p id="test">Hello world!\n</p></body></html>']
        source = '<html><head/><body><p id="test"/></body></html>'
        def simple_app(environ, start_response):
            start_response('200 OK', ('Content-type','text/html')) 
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGIHTMLTemplate(simple_app, source, format='xhtml11', engine='lxml')
        self.assertEqual(app({}, fake_response), final)

    def test_lwsgihtmltemplate_isstring(self):
        '''Tests if WSGIHTMLTemplate output is a string.'''
        source = '<html><head/><body><p id="test"/></body></html>'
        def simple_app(environ, start_response):
            start_response('200 OK', ('Content-type','text/html')) 
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGIHTMLTemplate(simple_app, source, format='xhtml10', engine='lxml')
        self.assertEqual(isinstance(app({}, fake_response)[0], str), True)

    def test_lwsgitemplate_isstring(self):
        '''Tests if WSGITemplate output is a string.'''
        source = '<html><head/><body><p id="test"/></body></html>'
        def simple_app(environ, start_response):            
            start_response('200 OK', ('Content-type','text/html'))            
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGITemplate(simple_app, source, engine='lxml')
        self.assertEqual(isinstance(app({}, fake_response)[0], str), True)

    def test_pickle(self):
        test = '<body><a href="atest" id="fieldtest"/><tr class="grouptest">' \
            '<td id="groupfield1"/><td id="groupfield2"/></tr></body>'
        serial = pickle.dumps(self.subcombotest)
        deserial = pickle.loads(serial)
        self.assertEqual(deserial.render(), test)

    def html_pickle(self):
        test = '<html><head><link href="test.css" ' \
        'type="text/css"><title id="title"><body><p id="content">' \
        '</body></head></html>'
        serial = pickle.dumps(self.htmlt)
        deserial = pickle.loads(serial)
        self.assertEqual(deserial.render(), test)          
        

if __name__ == '__main__': unittest.main()
