from formbuild.builder.field import FieldsBuilder
from webhelpers.rails.form_tag import *

class HtmlFields(FieldsBuilder):

    type = 'formbuild.builder.field.basic.HtmlFields'
    
    def date(self, *k, **p):
        return self.text(*k, **p)
        
    def static(self, name, value=None):
        if value == None:
            value = self._form.get_default(name)
        return str(value)
        
    # Straight from pylons.helpers with different names and with no defaults
    
    # XXX Should distinguish between single and combo and take different values
    def select(self, name, option_tags='', id=None, **options):
        return select(name, option_tags, id=id, **options)
        
    def options(self, options, selected_values):
        o = ''
        for op in options:
            o += self.option(op, selected_values)
        return o
    
    def text(self, name, value=None, id=None, *k, **options):
        if value == None:
            value = self._form.get_default(name)
        return text_field(name, value, id=id, **options)
    
    def hidden(self, name, value=None, id=None, **options):
        if value == None:
            value = self._form.get_default(name)
        return hidden_field(name, value, id=id, **options)
    
    def file(self, name, value=None, id=None, **options):
        if value == None:
            value = self._form.get_default(name)
        return file_field(name, value=value, id=id, **options)
    
    def password(self, name="password", value=None, id=None, **options):
        """Creates a password field
           Takes the same options as text_field """
        if value == None:
            value = self._form.get_default(name)
        return password_field(name, value, id=id, **options)
        
    def text_area(self, name, value=None, id=None, **options):
        """Creates a text input area"""
        if value == None:
            value = self._form.get_default(name)
        return text_area(name, content=value, id=id, **options)
    
    def check_box(self, name, value=None, checked=False, id=None, **options):
        """Creates a check box."""
        if value == None:
            value = self._form.get_default(name)
        return check_box(name, value, checked, id=id, **options)
    
    # XXX Should be radio group
    def radio(self, name, value, checked=False, id=None, **options):
        """Creates a radio button."""
        return radio_button(name, value, checked, id=id, **options)
    
    def submit(self, name='commit', value="", id=None, **options):
        """Creates a submit button with the text <tt>value</tt> as the caption."""
        if value == None:
            value = self._form.get_default(name)
        return submit(value=value, name=name, id=id, **options)
        
