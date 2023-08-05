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

'''Unit tests for webstring'''

import unittest
try:
    import cPickle as pickle
except ImportError:
    import pickle 
from webstring import TextTemplate, WSGITextTemplate

class Testwebstring(unittest.TestCase):

    '''Test class for webstring text template'''     

    # Add tests        
    groupend = '<tr class="tr1"><td id="td1"></td><td id="td2"></td></tr>' \
        '<tr class="tr2"><td id="td1"></td><td id="td2"></td></tr>'
    altgroupend = '<tr class="tr2"><td id="td1"></td><td id="td2"></td>' \
        '</tr><tr class="tr1"><td id="td1"></td><td id="td2"></td></tr>'
    subgroupend = '<td id="td1" /><td id="td1" />'        
    addtest = '<html><head><title id="title"></title></head></html><html><body>' \
        '<p id="content"></p></body></html>'
    altaddtest = '<html><body><p id="content" /></body><head>' \
        '<title id="title" /></head></html>'        
    field_add = '<p id="content" /><title id="title" />'
    field_group_add = '<title id="title" /><tr class="tr1"><td id="td1"></td>' \
        '<td id="td2"></td></tr>'
    root_group_add = '<html><head><title id="title"></title></head></html>' \
        '<tr class="tr1"><td id="td1"></td><td id="td2"></td></tr>'
    root_element_add = '<html><head><title id="title" /></head><p />' \
        '</html>'
    field_element_add = '<title id="title" /><p />'
    group_element_add = '<tr class="tr1"><td id="td1" />' \
        '<td id="td2" /></tr><p />'
    subfield_element_add = '<td id="td1" /><p />'
    # Mul tests
    multest = '<p id="content" /><p id="content" /><p id="content" />'
    root_mul = '<html><head><title id="title"></title></head><html><body>' \
        '<p id="content"></p></body></html></html><html><head><title id="title">' \
        '</title></head><html><body><p id="content"></p></body></html></html><html>' \
        '<head><title id="title"></title></head><html><body><p id="content"></p></body></html></html>'
    root_group_mul = '<tr class="tr1"><td id="td1"></td><td id="td2"></td>' \
        '</tr><tr class="tr1"><td id="td1"></td><td id="td2"></td></tr>' \
        '<tr class="tr1"><td id="td1"></td><td id="td2"></td></tr>'
    subfield_group_mul = '<td id="td1" /><td id="td1" /><td id="td1" />'
    # Mod tests
    modtest1 = '<html><head><title id="title">Test Page</title>' \
        '</head><body /></html>'        
    modtest2 = '<html><head><title id="title">Test Page</title></head>' \
    '<html><body><p id="content">Content Goes Here</p></body></html></html>'
    modtest3 = '<html><head><title id="title">Title</title></head><body>' \
        '<p id="content">Test1Test2</p><p id="content2">Test1Test2</p></body></html>'
    modtest5 = '<title id="title">Test Page</title>'
    groupmod = '<td id="td1">Test Page</td>'
    groupmod2 = '<table><tr class="tr1"><td id="td1">Test Page</td>' \
        '<td id="td2">Content Goes Here</td></tr></table>'
    groupmod3 = '<table><tr class="tr1"><td id="td1">Test1Test2</td>' \
        '<td id="td2">Test1Test2</td></tr></table>'
    # Pow tets
    powtest1 = '<p id="content">Test1</p><p id="content">Test2</p>'
    groupow = '<tr class="tr1"><td id="td1">1</td>' \
        '<td id="td2">2</td></tr><tr class="tr1"><td id="td1">3' \
        '</td><td id="td2">4</td></tr><tr class="tr1"><td id="td1">5' \
        '</td><td id="td2">6</td></tr>'
    # Templates
    modtemplate1 = TextTemplate('<html><head><title id="title">$title$</title></head>' \
        '<body /></html>')
    modtemplate3 = TextTemplate('<html><head><title id="title">$title$</title>' \
        '</head><body><p id="content">$content$</p><p id="content2">$content2$</p></body>' \
        '</html>')        
    gentemplate = TextTemplate('<html><head><title id="title">$title$</title></head><html><body>' \
        '<p id="content">$content$</p></body></html></html>')
    atemplate = TextTemplate('<html><head><title id="title">$title$</title></head>' \
        '</html>')
    btemplate = TextTemplate('<html><body><p id="content">$content$</p></body></html>')
    powtemplate = TextTemplate('<html><head /><body><p id="content">$content$</p>' \
        '</body></html>')
    agrouptest = TextTemplate('<table>$$tr1<tr class="tr1"><td id="td1">$td1$' \
        '</td><td id="td2">$td2$</td></tr>$$</table>')
    bgrouptest = TextTemplate('<table>$$tr2<tr class="tr2"><td id="td1">$td1$' \
        '</td><td id="td2">$td2$</td></tr>$$</table>')
    subcombotest = TextTemplate('<body><a id="fieldtest" href="atest">' \
        '$fieldtest$</a>$$grouptest<tr class="grouptest"><td id="groupfield1">' \
        '$groupfield1$</td><td id="groupfield2">$groupfield2$</td></tr>$$</body>')
    # Data structures        
    powdict = {'content1':'Test1', 'content2':'Test2'}
    powtup = ('<p id="content">Test1</p>', '<p id="content">Test2</p>')
    moddict = {'content':'Content Goes Here', 'title':'Test Page'}
    groupdict = {'td1':'Test Page', 'td2':'Content Goes Here'}
    modtup = ('Test Page', 'Content Goes Here')
    grouptup = (('1', '2'), ('3', '4'), ('5', '6'))
    groupowdict = {'2':['1', '2'], '4':['3', '4'], '6':['5', '6']}       

    def test_root_add(self):
        '''Tests addition of two root Templates.'''
        atst = self.atemplate + self.btemplate
        self.assertEqual(self.addtest, atst.render())

    def test_root_radd(self):
        '''Tests the right-side addition of two root Templates.'''
        final = '<html><body><p id="content"></p></body></html><html>' \
            '<head><title id="title"></title></head></html>'
        atst = self.btemplate + self.atemplate
        self.assertEqual(final, atst.render())

    def test_root_iadd(self):
        '''Tests the modifying addition of two root Templates.'''
        self.atemplate += self.btemplate
        self.assertEqual(self.addtest, self.atemplate.pipe())

    def test_field_add(self):
        '''Tests the addition of two fields.'''
        final = '<title id="title" /><p id="content" />'
        self.atemplate.title %= '<title id="title" />'
        self.btemplate.content %= '<p id="content" />'
        atst = self.atemplate.title + self.btemplate.content
        self.assertEqual(final, atst.render())

    def test_field_radd(self):
        '''Tests the right-side addition of two fields.'''
        self.atemplate.title %= '<title id="title" />'
        self.btemplate.content %= '<p id="content" />'
        atst = self.btemplate.content + self.atemplate.title
        self.assertEqual(self.field_add, atst.render())

    def test_field_iadd(self):
        '''Tests the modifying addition of two fields.'''
        self.atemplate.title %= '<title id="title" />'
        self.btemplate.content += self.atemplate.title
        self.assertEqual(self.field_add, self.btemplate.content.pipe())

    def test_group_add(self):
        '''Tests the addition of two groups.'''
        self.agrouptest.reset()
        atst = self.agrouptest.tr1 + self.bgrouptest.tr2
        self.assertEqual(self.groupend, atst.render())

    def test_group_radd(self):
        '''Tests the right-side addition of two groups.'''
        atst = self.bgrouptest.tr2 + self.agrouptest.tr1
        self.assertEqual(self.altgroupend, atst.render())

    def test_group_iadd(self):
        '''Tests the modifying addition of two groups.'''
        self.agrouptest.tr1 += self.bgrouptest.tr2
        self.assertEqual(self.groupend, self.agrouptest.tr1.pipe())

    def test_subfield_add(self):
        '''Tests the addition of two subfields.'''
        self.bgrouptest.tr2.td1 %= '<td id="td1" />'
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        atst = self.agrouptest.tr1.td1 + self.bgrouptest.tr2.td1
        self.assertEqual(self.subgroupend, atst.render())

    def test_subfield_radd(self):
        '''Tests the right-side addition of two subfields.'''
        final = '<td id="td1" /><td id="td1" />'
        self.bgrouptest.tr2.td1 %= '<td id="td1" />'
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        atst = self.bgrouptest.tr2.td1 + self.agrouptest.tr1.td1
        self.assertEqual(final, atst.render())

    def test_subfield_iadd(self):
        '''Tests the modifying addition of two subfields.'''
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        self.bgrouptest.tr2.td1 %= '<td id="td1" />'
        self.agrouptest.tr1.td1 += self.bgrouptest.tr2.td1
        self.assertEqual(self.subgroupend, self.agrouptest.tr1.td1.pipe())

    def test_field_root_iadd(self):
        '''Tests the modifying addition of a field and a root TextTemplate.'''
        final = '<title id="title" /><html><body><p id="content"></p></body></html>'
        self.atemplate.title += self.btemplate
        self.assertEqual(final, self.atemplate.title.pipe())

    def test_field_group_iadd(self):
        '''Tests the modifying addition of a field and group.'''
        self.atemplate.title %= '<title id="title" />'
        self.atemplate.title += self.agrouptest.tr1
        self.assertEqual(self.field_group_add,
            self.atemplate.title.pipe())

    def test_field_subfield_iadd(self):
        '''Tests the modifying addition of a field and subfield.'''
        final = '<title id="title" /><td id="td1" />'
        self.atemplate.title %= '<title id="title" />'
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        self.atemplate.title += self.agrouptest.tr1.td1
        self.assertEqual(final, self.atemplate.title.pipe())                

    def test_root_field_iadd(self):
        '''Tests the modifying addition of a root TextTemplate and a field.'''
        final = '<html><body><p id="content"></p></body></html>' \
        '<title id="title" />'
        self.atemplate.title %= '<title id="title" />'
        self.btemplate += self.atemplate.title
        self.assertEqual(final, self.btemplate.pipe())

    def test_root_group_iadd(self):
        '''Tests the modifying addition of a root TextTemplate and a group.'''
        self.atemplate.reset()
        self.agrouptest.reset()
        self.atemplate += self.agrouptest.tr1
        self.assertEqual(self.root_group_add, self.atemplate.pipe())

    def test_root_subfield_iadd(self):
        '''Tests the modifying addition of a root TextTemplate and subfield.'''
        final = '<html><head><title id="title"></title></head></html><td id="td1" />'
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        self.atemplate += self.agrouptest.tr1.td1
        self.assertEqual(final, self.atemplate.pipe())

    def test_group_subfield_iadd(self):
        '''Tests the modifying addition of one group and one subfield.'''
        final = '<tr class="tr1"><td id="td1"></td><td id="td2"></td>' \
            '</tr><td id="td1"></td>'
        self.bgrouptest.tr2.td1 %= '<td id="td1"></td>'
        self.agrouptest.tr1 += self.bgrouptest.tr2.td1
        self.assertEqual(final, self.agrouptest.tr1.pipe())

    def test_subfield_group_iadd(self):
        '''Tests the modifying addition of one subfield and one group.'''
        final = '<td id="td1" /><tr class="tr1"><td id="td1"></td><td id="td2"></td></tr>'
        self.bgrouptest.tr2.td1 += self.agrouptest.tr1
        self.assertEqual(final, self.bgrouptest.tr2.td1.pipe())            

    def test_root_radd_raise(self):
        '''Raises TypeError if wrong type right-side added to root TextTemplate.'''
        def tempfunc(): return [1, 1, 1] + self.atemplate
        self.assertRaises(TypeError, tempfunc)

    def test_root_iadd_raise(self):
        '''Raises TypeError if wrong type is added to root TextTemplate.'''
        def tempfunc():
            atst = self.atemplate.default
            atst += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)

    def test_field_radd_raise(self):
        '''Raises TypeError if wrong type is right-side added to field.'''
        def tempfunc():
            return [1, 1, 1] + self.atemplate.title
        self.assertRaises(TypeError, tempfunc)

    def test_field_iadd_raise(self):
        '''Raises TypeError if wrong type is modifyingly added to field.'''
        def tempfunc():
            atst = self.atemplate.default
            atst.title += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)

    def test_group_radd_raise(self):
        '''Raises TypeError if wrong type is right-side added to group.'''
        def tempfunc(): return [1, 1, 1] + self.agrouptest.tr1
        self.assertRaises(TypeError, tempfunc)

    def test_group_iadd_raise(self):
        '''Raises TypeError if wrong type is modifyingly added to group.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1 += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)

    def test_subfield_radd_raise(self):
        '''Raises TypeError if wrong type is right-side added to subfield.'''
        def tempfunc(): return [1, 1, 1] + self.agrouptest.tr1.td1
        self.assertRaises(TypeError, tempfunc)

    def test_subfield_iadd_raise(self):
        '''Raises TypeError if wrong type is modifyingly added to subfield.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.td1 += [1, 1, 1]
        self.assertRaises(TypeError, tempfunc)    

    def test_root_rmul(self):
        '''Tests repetition of a root TextTemplate with number on the right.'''
        atst = 3 * self.gentemplate
        self.assertEqual(self.root_mul, atst.render())

    def test_root_imul(self):
        '''Tests modifying repetition of a root TextTemplate.'''
        self.gentemplate *= 3
        self.assertEqual(self.root_mul, self.gentemplate.pipe())

    def test_field_mul(self):
        '''Tests the repetition of a field.'''
        self.gentemplate.content %= '<p id="content" />'
        atst = self.gentemplate.content * 3
        self.assertEqual(self.multest, atst.render())

    def test_field_rmul(self):
        '''Tests repetition of a field with the number on the right.'''
        self.gentemplate.content %= '<p id="content" />'
        atst = 3 * self.gentemplate.content
        self.assertEqual(self.multest, atst.render())

    def test_field_imul(self):
        '''Tests modifying repetition of a field.'''
        self.gentemplate.content %= '<p id="content" />'
        self.gentemplate.content *= 3
        self.assertEqual(self.multest, self.gentemplate.content.pipe())        

    def test_group_rmul(self):
        '''Tests repetition of a group with the number on the right side.'''
        atst = 3 * self.agrouptest.tr1
        self.assertEqual(self.root_group_mul, atst.render())

    def test_group_imul(self):
        '''Tests modifying repetition of a group.'''
        self.agrouptest.tr1 *= 3            
        self.assertEqual(self.root_group_mul, self.agrouptest.tr1.pipe())

    def test_subfield_rmul(self):
        '''Tests repetition of a subfield with the number on the right side.'''
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        atst = 3 * self.agrouptest.tr1.td1
        self.assertEqual(self.subfield_group_mul, atst.render())

    def test_subfield_mul(self):
        '''Tests the repetition of a subfield.'''
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        atst = self.agrouptest.tr1.td1 * 3
        self.assertEqual(self.subfield_group_mul, atst.render())    

    def test_subfield_imul(self):
        '''Tests modifying repetition of a subfield.'''
        self.agrouptest.tr1.td1 %= '<td id="td1" />'
        self.agrouptest.tr1.td1 *= 3            
        self.assertEqual(self.subfield_group_mul,
            self.agrouptest.tr1.td1.pipe())

    def test_field_imul_rep(self):
        '''Tests restraint on a max modifying repetition of a field.'''
        def tempfunc():
            atst = self.gentemplate.default
            atst.content.max = 2
            atst.content *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_root_imul_rep(self):
        '''Tests restraint on max modifying repetition of a root TextTemplate.'''
        def tempfunc():
            atst = self.gentemplate.default
            atst.max = 2
            atst *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_group_imul_rep(self):
        '''Tests restraint on max modifying repetition of a field.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.max = 2
            atst.tr1 *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_subfield_imul_rep(self):
        '''Tests restraint on max modifying repetition of a subfield.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.td1.max = 2
            atst.tr1.td1 *= 3
        self.assertRaises(TypeError, tempfunc)

    def test_field_string_mod(self):
        '''Tests a modifying string substitution of a field.'''
        atst = self.modtemplate1.title % '<title id="title">Test Page</title>'
        self.assertEqual(atst.render(), self.modtest5)

    def test_field_string_imod(self):
        '''Tests a modifying string substitution of a field.'''
        self.modtemplate1.title %= '<title id="title">Test Page</title>'
        self.assertEqual(self.modtest5, self.modtemplate1.title.pipe())

    def test_subfield_string_imod(self):
        '''Tests a modifying string substitution of a subfield.'''
        self.agrouptest.tr1.td1 %= '<td id="td1">Test Page</td>'
        self.assertEqual(self.groupmod, self.agrouptest.tr1.td1.pipe())

    def test_root_string_mod(self):
        '''Raises TypeError if string passed to a root TextTemplate.'''
        def tempfunc(): return self.gentemplate % 'Test Page'
        self.assertRaises(TypeError, tempfunc)

    def test_field_mod_str_wrongtype(self):
        '''Raises TypeError if wrong type passed to a field.'''
        def tempfunc(): return self.gentemplate.content % ['Test Page']
        self.assertRaises(TypeError, tempfunc)            

    def test_root_group_str_mod_toofew(self):
        '''Raises TypeError if string passed to root containing only group.'''
        def tempfunc(): return self.agrouptest % 'Test Page'
        self.assertRaises(TypeError, tempfunc)

    def test_field_group_str_mod_toofew(self):
        '''Raises TypeError if string passed to a group.'''
        def tempfunc(): return self.agrouptest.tr1 % 'Test Page'
        self.assertRaises(TypeError, tempfunc)        

    def test_root_tuple_imod(self):
        '''Tests a modifying tuple substitution of a root TextTemplate.'''
        self.gentemplate %= self.modtup
        self.assertEqual(self.modtest2, self.gentemplate.pipe())

    def test_group_tuple_imod(self):
        '''Tests a modifying tuple substitution of a group.'''
        self.agrouptest.tr1 %= self.modtup
        self.assertEqual(self.groupmod2, self.agrouptest.pipe())            

    def test_root_tuple_tuple_imod_expand(self):
        '''Tests a modifying tuple tuple substitution/expansion of root.'''
        self.modtemplate3 %= ('Title', ('Test1', 'Test2'),
            ('Test1', 'Test2'))
        self.assertEqual(self.modtest3, self.modtemplate3.pipe())

    def test_group_tuple_tuple_imod_expand(self):
        '''Tests a modifying tuple tuple substitution/expansion of a group.'''
        self.agrouptest.tr1 %= (('Test1', 'Test2'), ('Test1', 'Test2'))
        self.assertEqual(self.groupmod3, self.agrouptest.pipe())

    def test_root_tuple_mod_wrongtype(self):
        '''Raises TypeError if wrong type in tuple is subbed into root.'''
        def tempfunc(): return self.gentemplate % (set(['Test Page']), )
        self.assertRaises(TypeError, tempfunc)

    def test_group_tuple_mod_wrongtype(self):
        '''Raises TypeError if wrong type in tuple is subbed into group.'''
        def tempfunc(): return self.agrouptest.tr1 % (set(['Test Page']), )
        self.assertRaises(TypeError, tempfunc)            

    def test_root_tuple_mod_toomany(self):
        '''Raises TypeError if too many items in tuple are subbed in root.'''
        def tempfunc(): return self.gentemplate % ('Test', 'Test', 'Too Many')
        self.assertRaises(TypeError, tempfunc)

    def test_group_tuple_mod_toomany(self):
        '''Raises TypeError if too many items in tuple are subbed in group.'''
        def tempfunc(): return self.agrouptest.tr1 % ('Test', 'Test', 'Test')
        self.assertRaises(TypeError, tempfunc)              

    def test_root_tuple_mod_toofew(self):
        '''Raises TypeError if too few items in tuple are subbed into root.'''
        def tempfunc(): return self.gentemplate % ('Test Page')
        self.assertRaises(TypeError, tempfunc)

    def test_group_tuple_mod_toofew(self):
        '''Raises TypeError if too few items in tuple are subbed into group.'''
        def tempfunc(): return self.agrouptest.tr1 % ('Test Page')
        self.assertRaises(TypeError, tempfunc)        

    def test_root_dict_imod(self):
        '''Tests a modifying dictionary substitution of a root TextTemplate.'''
        self.gentemplate %= self.moddict
        self.assertEqual(self.modtest2, self.gentemplate.pipe())

    def test_group_dict_imod(self):
        '''Tests a modifying dict substitution of a group TextTemplate.'''
        self.agrouptest.tr1 %= self.groupdict
        self.assertEqual(self.groupmod2, self.agrouptest.pipe())

    def test_root_dict_tuple_imod_expand(self):
        '''Tests a modifying dictionary tuple sub/expansion of a root.'''
        self.modtemplate3 %= {'title':'Title', 'content':('Test1', 'Test2'),
            "content2":('Test1', 'Test2')}
        self.assertEqual(self.modtest3, self.modtemplate3.pipe())

    def test_group_dict_tuple_imod_expand(self):
        '''Tests a modifying dict tuple substitution/expansion of a group.'''
        self.agrouptest.tr1 %= {'td1':('Test1', 'Test2'),
            'td2':('Test1', 'Test2')}
        self.assertEqual(self.groupmod3, self.agrouptest.pipe())

    def test_root_dict_mod_wrongtype(self):
        '''Raises TypeError if wrong type in a dict are subbed into a root.'''
        def tempfunc(): return self.gentemplate % {'content':set(['Test'])}
        self.assertRaises(TypeError, tempfunc)

    def test_group_dict_mod_wrongtype(self):
        '''Raises TypeError if wrong type in a dict are subbed into a group.'''
        def tempfunc(): return self.agrouptest.tr1 % {'td1':set(['Test Page'])}
        self.assertRaises(TypeError, tempfunc)            

    def test_root_dict_mod_toomany(self):
        '''Raises TypeError if too many items in dict are subbed into root.'''
        def tempfunc():
            return self.gentemplate % {'content':'Content Goes Here',
                'title':'Test Page', 'test':'Too many'}
        self.assertRaises(TypeError, tempfunc)

    def test_group_dict_mod_toomany(self):
        '''Raises TypeError if too many items in dict are subbed into group.'''
        def tempfunc():
            return self.agrouptest.tr1 % {'td1':'Content Goes Here',
                'td2':'Test Page', 'td3':'Too many'}
        self.assertRaises(TypeError, tempfunc)            

    def test_root_dict_mod_toofew(self):
        '''Raises TypeError if too few items in dict are subbed into root.'''
        def tempfunc(): return self.gentemplate % {'content':'Content'}
        self.assertRaises(TypeError, tempfunc)

    def test_group_dict_mod_toofew(self):
        '''Raises TypeError if too few items in dict are subbed into group.'''
        def tempfunc(): return self.gentemplate % {'content':'Content'}
        self.assertRaises(TypeError, tempfunc)

    def test_field_pow(self):
        '''Tests a expansion of a field.'''
        atst = self.powtemplate.content ** self.powtup
        self.assertEqual(self.powtest1, atst.render())

    def test_field_ipow(self):
        '''Tests a modifying expansion of a field.'''
        self.powtemplate.content **= self.powtup
        self.assertEqual(self.powtest1, self.powtemplate.content.pipe())

    def test_group_ipow(self):
        '''Tests a modifying expansion of a group.'''
        self.agrouptest.tr1 **= self.grouptup
        self.assertEqual(self.groupow, self.agrouptest.tr1.pipe())

    def test_field_pow_rep(self):
        '''Raises TypeError if field expansion exceeds max repetitions.'''
        def tempfunc():
            atst = self.powtemplate.default
            atst.content.max = 1
            atst.content ** self.powtup
        self.assertRaises(TypeError, tempfunc)

    def test_group_pow_rep(self):
        '''Raises TypeError if group expansion exceeds max repetitions.'''
        def tempfunc():
            atst = self.agrouptest.default
            atst.tr1.max = 1
            return atst.tr1 ** self.grouptup
        self.assertRaises(TypeError, tempfunc)                       

    def test_field_pow_wrongtype(self):
        '''Raises TypeError if wrong type passed in for field expansion.'''
        def tempfunc(): return self.powtemplate ** 'This is a test.'
        self.assertRaises(TypeError, tempfunc)

    def test_group_pow_wrongtype(self):
        '''Raises TypeError if wrong type passed in for group expansion.'''
        def tempfunc(): return self.agrouptest.tr1 ** 'This is a test.'
        self.assertRaises(TypeError, tempfunc)            

    def test_field_delattr_dict(self):
        '''Tests deletion of field attributes from internal dict.'''
        atst = self.btemplate.default
        del atst.content
        self.assertEqual(False, atst._fielddict.has_key('content'))

    def test_group_delattr_dict(self):
        '''Tests deletion of group attributes from internal dict.'''
        atst = self.agrouptest.default
        del atst.tr1
        self.assertEqual(False, atst._fielddict.has_key('tr1'))

    def test_subfield_delattr_dict(self):
        '''Tests deletion of group attributes from internal dict.'''
        atst = self.agrouptest.default
        del atst.tr1.td1
        self.assertEqual(False, atst.tr1._fielddict.has_key('td1'))

    def test_field_delattr(self):
        '''Tests deletion of field attributes from internal list.'''
        atst = self.btemplate.default
        del atst.content
        self.assertEqual(False, 'content' in atst)

    def test_group_delattr(self):
        '''Tests deletion of group attributes from internal list.'''
        atst = self.agrouptest.default
        del atst.tr1
        self.assertEqual(False, 'tr1' in atst)

    def test_subfield_delattr(self):
        '''Tests deletion of subfield attributes from internal list.'''
        atst = self.agrouptest.default
        del atst.tr1.td1
        self.assertEqual(False, 'td1' in atst.tr1)

    def test_field_getitem(self):
        '''Tests getting field contents by index.'''
        atst = self.btemplate.default
        atst.content %= 'Test'
        self.assertEqual('Test', atst[0].text)

    def test_group_getitem(self):
        '''Tests getting group contents by index.'''
        atst = self.agrouptest.default
        self.assertEqual(True, hasattr(atst[0], 'td1'))

    def test_subfield_getitem(self):
        '''Tests getting subfield contents by index.'''
        atst = self.agrouptest.default
        atst.tr1.td1 %= 'Test'
        self.assertEqual('Test', atst[0][0].text)

    def test_field_setitem(self):
        '''Tests setting field contents by index.'''
        atst = self.btemplate.default
        atst[0] %= 'Test'
        self.assertEqual('Test', atst[0].text)

    def test_group_setitem(self):
        '''Tests setting group contents by index.'''
        atst = self.agrouptest.default
        atst[0].id = 'Test'
        self.assertEqual('Test', atst[0].id)

    def test_subfield_setitem(self):
        '''Tests setting subfield contents by index.'''
        atst = self.agrouptest.default
        atst[0][0] %= 'Test'
        self.assertEqual('Test', atst[0][0].text)
        
    def test_field_delitem(self):
        '''Tests deleting fields by index.'''
        atst = self.btemplate.default
        del atst[0]
        self.assertEqual(False, hasattr(atst, 'content'))

    def test_group_delitem(self):
        '''Tests deleting groups by index.'''
        atst = self.agrouptest.default
        del atst[0]
        self.assertEqual(False, hasattr(atst, 'tr1'))

    def test_subfield_delitem(self):
        '''Tests deleting subfields by index.'''
        atst = self.agrouptest.default
        del atst[0][0]
        self.assertEqual(False, hasattr(atst.tr1, 'td1'))

    def test_field_getitem_key(self):
        '''Tests getting field contents by key.'''
        atst = self.btemplate.default
        atst.content %= 'Test'
        self.assertEqual('Test', atst['content'].text)

    def test_group_getitem_key(self):
        '''Tests getting group contents by key.'''
        atst = self.agrouptest.default
        self.assertEqual(True, hasattr(atst['tr1'], 'td1'))

    def test_group_field_delitem_key(self):
        '''Tests deleting subfield by key.'''
        atst = self.agrouptest.default
        del atst['tr1']['td1']
        self.assertEqual(False, hasattr(atst.tr1, 'td1'))        

    def test_root_len(self):
        '''Tests getting number of fields in a root TextTemplate.'''
        atst = self.btemplate.default
        self.assertEqual(1, len(atst))

    def test_group_len(self):
        '''Tests getting number of fields in a group.'''
        atst = self.agrouptest.default
        self.assertEqual(2, len(atst.tr1))

    def test_contains_true(self):
        '''Tests if a field of a certain name is in a root TextTemplate.'''
        atst = self.btemplate.default
        val = 'content' in atst
        self.assertEqual(True, val)

    def test_contains_false(self):
        '''Tests if a field of a certain name is not in a root TextTemplate.'''
        atst = self.btemplate.default
        val = 'content1' in atst
        self.assertEqual(False, val)

    def test_iter_false(self):
        '''Tests if an iterator finds false values.'''
        atst = self.btemplate.default
        val = False
        for i in atst:
            if i.__name__ == 'content1': val = True
        self.assertEqual(False, val)

    def test_iter_true(self):
        '''Tests if an iterator finds true values.'''
        atst = self.btemplate.default
        val = False
        for i in atst:
            if i.__name__ == 'content': val = True
        self.assertEqual(True, val)

    def test_iter_assign(self):
        '''Tests if an iterator assigns correctly.'''
        atst = self.btemplate.default
        for i in atst: i %= 'Test'
        self.assertEqual('Test', atst.content.text)

    def test_root_max(self):
        '''Tests max assignment on a root.'''
        atst = self.gentemplate.default
        atst.max = 100
        self.assertEqual(200, atst.title.max + atst.content.max)

    def test_group_max(self):
        '''Tests max assignment on a group.'''
        atst = self.agrouptest.default
        atst.max = 100
        self.assertEqual(200, atst.tr1.td1.max + atst.tr1.td2.max)           

    def test_auto_auto_off_hasattr(self):
        '''Tests if auto turns off magical attributes for elements.'''
        atst = TextTemplate('<html><head><title id="title">$title</title></head><body>' \
            '<p id="content">$content</p></body></html>', False)
        self.assertEqual(hasattr(atst, 'title'), False)    

    def test_root_append(self):
        '''Tests appending a field to a root TextTemplate.'''
        final = '<html><head><title id="title"><title id="title" /></title></head></html>'
        self.atemplate.title %= '<title id="title" />'
        self.atemplate.append(self.atemplate.title.default)
        self.assertEqual(final, self.atemplate.pipe())

    def test_field_append(self):
        '''Tests appending a root TextTemplate to a field.'''
        final = '<html><head><title id="title"><html><head>' \
            '<title id="title"></title></head></html></title></head></html>'      
        self.atemplate.title.append(self.atemplate.default)
        self.assertEqual(final, self.atemplate.pipe())

    def test_group_append(self):
        '''Tests appending a root TextTemplate to a group.'''
        final = '<table><tr class="tr1"><td id="td1"></td><td id="td2"></td>' \
            '</tr><table><tr class="tr1"><td id="td1"></td><td id="td2"></td>' \
            '</tr></table></table>' 
        self.agrouptest.tr1.append(self.agrouptest.default)
        self.assertEqual(final, self.agrouptest.pipe())

    def test_group_append_reset_test(self):
        '''Tests appending a root TextTemplate to a group and reseting.'''
        final = '<table><tr class="tr1"><td id="td1"></td><td id="td2"></td>' \
            '</tr><table><tr class="tr1"><td id="td1"></td><td id="td2"></td>' \
            '</tr></table></table>'   
        self.agrouptest.tr1.append(self.agrouptest.default)
        test = self.agrouptest.render()
        self.agrouptest.tr1.reset()
        self.assertEqual(final, test)  

    def test_root_append_wrongtype(self):
        '''Raises TypeError if appending a wrong type to a root TextTemplate.'''
        def tempfunc(): self.atemplate.append(['p'])
        self.assertRaises(TypeError, tempfunc)            

    def test_group_append_wrongtype(self):
        '''Raises TypeError if appending a wrong type to a group.'''
        def tempfunc(): self.agrouptest.tr1.append(['p'])
        self.assertRaises(TypeError, tempfunc)            

    def test_field_append_wrongtype(self):
        '''Raises TypeError if appending the wrong type to a field.'''
        def tempfunc(): self.atemplate.title.append(['p'])
        self.assertRaises(TypeError, tempfunc) 

    def test_exclude(self):
        '''Tests exclusion on a root TextTemplate.'''
        a = TextTemplate()
        a.exclude('td1', 'td2')
        a.fromstring('<tr><td id="td1">$td1$</td><td id="td2">$td2$</td><td id="td3">$td3$</td></tr>')
        self.assertEqual(True, len(a) == 1)            

    def test_exclude_live(self):
        '''Tests exclusion on a live root TextTemplate.'''
        testfilter = TextTemplate('<table>$$tr1 <tr class="tr1"><td id="td1">$td1$' \
            '</td><td id="td2">$td2$</td></tr>$$<p id="r">$r$</p></table>')
        testfilter.exclude('tr1', 'r')
        self.assertEqual(True, len(testfilter) == 0)

    def test_exclude_group(self):
        '''Tests exclusion on a group.'''
        a = TextTemplate()
        a.exclude('tr1')
        a.fromstring('<table>$$tr1 <tr class="tr1"><td id="td1">$td1$' \
            '</td><td id="td2">$td2$</td></tr>$$<p id="r">$r$</p></table>')
        self.assertEqual(True, len(a) == 1)            

    def test_exclude_live_group(self):
        '''Tests exclusion on a live group.'''
        testfilter = TextTemplate('<table>$$tr1 <tr class="tr1"><td id="td1">$td1$' \
            '</td><td id="td2">$td2$</td></tr>$$<p id="r">$r$</p></table>')
        testfilter.exclude('td1', 'td2')
        self.assertEqual(True, len(testfilter) == 1)        

    def test_exclude_wrongtype(self):
        '''Raises TypeError if wrong type included.'''
        def tempfunc(): self.agrouptest.exclude(['eeee'])
        self.assertRaises(AttributeError, tempfunc)             

    def test_root_include(self):
        '''Tests inclusion on a TextTemplate.'''
        testfilter = TextTemplate()
        testfilter.exclude('td1')
        testfilter.fromstring('<tr><td id="td1">$td1$</td><td id="td2">$td2$</td></tr>')
        testfilter.include('td1')
        self.assertEqual(True, hasattr(testfilter, 'td1'))

    def test_include_live(self):
        '''Tests inclusion on a live TextTemplate.'''
        testfilter = TextTemplate('<table>$$tr1 <tr class="tr1"><td id="td1">$td1$' \
            '</td><td id="td2">$td2$</td></tr>$$<p id="r">$r$</p></table>')
        testfilter.exclude('tr1', 'r')
        testfilter.include('tr1', 'r')
        self.assertEqual(True, len(testfilter) == 2)

    def test_include_group(self):
        '''Tests inclusion on a group.'''
        a = TextTemplate()
        a.exclude('td1', 'td2')
        a.fromstring('<table>$$tr1 <tr class="tr1"><td id="td1">$td1$' \
            '</td><td id="td2">$td2$</td></tr>$$<p id="r">$r$</p></table>')
        a.include('td1', 'td2')
        self.assertEqual(True, len(a.tr1) == 2)            

    def test_include_live_group(self):
        '''Tests inclusion on a live group.'''
        testfilter = TextTemplate('<table>$$tr1 <tr class="tr1"><td id="td1">$td1$' \
            '</td><td id="td2">$td2$</td></tr>$$<p id="r">$r$</p></table>')
        testfilter.exclude('td1', 'td2')
        testfilter.include('td1', 'td2')
        self.assertEqual(True, len(testfilter.tr1) == 2)         

    def test_include_wrongtype(self):
        '''Tests if inclusion raises an exception with wrong type passed.'''
        def tempfunc(): self.agrouptest.include(['eeee'])
        self.assertRaises(TypeError, tempfunc) 
       
    def test_no_empty_group(self):
        '''Tests if empty groups are properly pruned.'''
        testfilter = TextTemplate()
        testfilter.exclude('td1')
        testfilter.fromstring('<div>$$tr1 <tr class="tr1">' \
            '<td id="td1">$td1</td></tr>$$</table></div>')
        testfilter.include('td1')
        self.assertEqual(False, hasattr(testfilter, 'thing')) 

    def test_wsgitemplate(self):
        '''Tests for correct text output.'''
        final = ['<html><head /><body><p id="test">Hello world!\n</p></body>' \
            '</html>']
        source = '<html><head /><body><p id="test">$test$</p></body></html>'
        def simple_app(environ, start_response):
            start_response('200 OK', ('Content-type','text/html'))              
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGITextTemplate(simple_app, source)
        self.assertEqual(app({}, fake_response), final)     

    def test_wsgitexttemplate_isstring(self):
        '''Tests if WSGITextTemplate output is a string.'''
        source = '<html><head/><body><p id="test">$test$</p></body></html>'
        def simple_app(environ, start_response):            
            start_response('200 OK', ('Content-type','text/html'))            
            return {'test':'Hello world!\n'} 
        def fake_response(status, response, ex_info=None): 
            pass
        app = WSGITextTemplate(simple_app, source)
        self.assertEqual(isinstance(app({}, fake_response)[0], str), True)         

    def test_pickle(self):
        test = '<body><a id="fieldtest" href="atest">' \
        '</a><tr class="grouptest"><td id="groupfield1">' \
        '</td><td id="groupfield2"></td></tr></body>'
        serial = pickle.dumps(self.subcombotest)
        deserial = pickle.loads(serial)
        self.assertEqual(deserial.render(), test)

    def test_delattr_root_template(self):
        e = TextTemplate('$test$ is a $test2$')
        del e.test
        self.assertEqual(e._template, u' is a %s')

    def test_delattr_group_template(self):
        e = TextTemplate('$$test a$$is a $test2$')
        del e.test
        self.assertEqual(e._template, u'is a %s')
        

if __name__ == '__main__': unittest.main()
