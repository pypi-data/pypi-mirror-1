from unittest import TestCase
import unittest
import pkg_resources

pkg_resources.require('FormBuild')

from formbuild.builder.field import *
from formbuild import *

class TestFieldsSimpleHTML(TestCase):
    
    def setUp(self):
        form = Form()
        self.field = form.field
    
    def test_dropdown(self):
        self.assertEqual(
            '<select name="test"><option value="1" selected="selected">a</option>\n</select>', 
            self.field.dropdown(name='test', values=[[1,'a']], value=1)
        )


    def test_select(self):
        self.assertEqual(
            '<select name="test"></select>', 
            self.field.select(name='test', option_tags='')
        )
        self.assertEqual(
            '<select name="test"><option value="1" selected="selected">a</option></select>', 
            self.field.select(name='test', option_tags=self.field.option(option=[1,'a'], selected_values=[1,2,3]))
        )

    def test_option(self):
        self.assertEqual(
            '<option value="1" selected="selected">a</option>', 
            self.field.option(option=[1,'a'], selected_values=[1,2,3]),
        )
        self.assertEqual(
            '<option value="1" selected="selected">a</option>', 
            self.field.option(option=[1,'a'], selected_values=1)
        )
        self.assertEqual(
            '<option value="1" selected="selected">1</option>', 
            self.field.option(option='1', selected_values=[1,2,3])
        )

    def test_text(self):
        self.assertEqual(
            '<input name="test" type="text" value="value" />', 
            self.field.text(name='test', value='value')
        )

    def test_hidden(self):
        self.assertEqual(
            '<input name="test" type="hidden" value="value" />', 
            self.field.hidden(name='test', value='value')
        )

    def test_file(self):
        self.assertEqual(
            '<input name="test" type="file" value="value" />', 
            self.field.file(name='test', value='value')
        )

    def test_password(self):
        self.assertEqual(
            '<input name="test" type="password" value="value" />', 
            self.field.password(name='test', value='value')
        )
        
    def test_submit(self):
        self.assertEqual(
            '<input name="test" type="submit" value="value" />', 
            self.field.submit(name='test', value='value')
        )
        
    def test_text_area(self,):
        self.assertEqual(
            '<textarea name="test">value</textarea>', 
            self.field.text_area(name='test', value='value')
        )

    def test_check_box(self,):
        self.assertEqual(
            '<input name="test" type="checkbox" value="value" />', 
            self.field.check_box(name='test', value='value')
        )
        
    def test_radio_button(self,):
        self.assertEqual(
            '<input name="test" type="radio" value="value" />', 
            self.field.radio(name='test', value='value')
        )

class TestFieldsCompoundHTML(TestCase):
    
    def setUp(self):
        from formbuild import Form
        from formbuild.builder.field import basic
        from formbuild.builder.field import compound
        
        class MyForm(Form):
            field = basic.HtmlFields(), compound.HtmlFields()
            
        form = MyForm()
        self.field = form.field
    
    def test_check_box_group(self):
        self.assertEqual(
            """<input type="checkbox" name="test" value="0" /> holly
<input type="checkbox" name="test" value="1" checked /> ivy""", 

            self.field.check_box_group(name='test', options=[['0','holly'],['1','ivy']], values='1')
        )
        self.assertEqual(
            """<input type="checkbox" name="test" value="0" /> holly
<input type="checkbox" name="test" value="1" /> ivy""", 
            self.field.check_box_group(name='test', options=[['0','holly'],['1','ivy']], values=[])
        )
        
    def test_frozen(self):

        from formbuild import Form
        from formbuild.modifier import Frozen
        from formbuild.builder.field import basic
        from formbuild.builder.field import compound
        
        class MyForm(Form):
            field = Frozen(basic.HtmlFields(), compound.HtmlFields())
            
        form = MyForm()
        self.assertEqual('b', form.field.text(name='a', jim='jim_val', value="b"))
        self.assertEqual('d', form.field.text('c','d'))
        self.assertEqual('', form.field.text('c'))

    def test_build(self):

        from formbuild import Form
        from formbuild.modifier import Build
        from formbuild.builder.field import basic
        from formbuild.builder.field import compound
        
        class MyForm(Form):
            field = Build(basic.HtmlFields(), compound.HtmlFields())
            
        form = MyForm()
        self.assertEqual(
            {'jim': 'jim_val', 'name': 'a', 'value': 'b'},
            form.field.text(name='a', jim='jim_val', value="b")
        )
        self.assertEqual({'name': 'c', 'value': 'd'},form.field.text('c','d'))
        self.assertEqual({'name': 'c'},form.field.text('c'))
        self.assertRaises(TypeError, form.field.text,'c','d',value='e')
        self.assertRaises(TypeError, form.field.text)

    def test_capture(self):

        from formbuild import Form
        from formbuild.modifier import Capture
        from formbuild.builder.field import basic
        from formbuild.builder.field import compound
        
        class MyForm(Form):
            field = Capture(basic.HtmlFields(), compound.HtmlFields())
            
        form = MyForm()
        self.assertEqual([],form.field.captured)
        self.assertEqual(None,form.field.text(name='a', jim='jim_val', value="b"))
        self.assertEqual([['formbuild.builder.field.basic.HtmlFields.text', {'jim': 'jim_val', 'name': 'a', 'value': 'b'}]],form.field.captured)

    def test_capture_and_return(self):

        from formbuild import Form
        from formbuild.modifier import CaptureAndReturn
        from formbuild.builder.field import basic
        from formbuild.builder.field import compound
        
        class MyForm(Form):
            field = CaptureAndReturn(basic.HtmlFields(), compound.HtmlFields())
            
        form = MyForm()
        self.assertEqual([],form.field.captured)
        self.assertEqual('<input jim="jim_val" name="a" type="text" value="b" />',form.field.text(name='a', jim='jim_val', value="b"))
        self.assertEqual([['formbuild.builder.field.basic.HtmlFields.text', {'jim': 'jim_val', 'name': 'a', 'value': 'b'}]],form.field.captured)

    def test_create(self):
        from formbuild import Form
        from formbuild.creator import CaptureDataRecreator
        creator = CaptureDataRecreator(Form())
        r = creator.create(
            [['formbuild.builder.field.basic.HtmlFields.text', {'name': 'one'}]])
        self.assertEqual('<input name="one" type="text" />','\n'.join(r))


        
if __name__ == '__main__':
    suite = [unittest.makeSuite(TestFieldsSimpleHTML), unittest.makeSuite(TestFieldsCompoundHTML)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
