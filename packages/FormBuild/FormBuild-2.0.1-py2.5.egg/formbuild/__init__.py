# -*- coding: utf-8 -*-

"""\

FormBuild 2.0 is a complete re-write of FormBuild 0.1 with a vastly simplified
API focusing on the core use case and with automatic variable escaping built in
to help prevent XSS attacks. The new API supports all the features of the old
one but is easier to understand.

"""

import warnings
from webhelpers.html.tags import checkbox, file, hidden, image, password, radio, select, submit, text, textarea
from webhelpers.html.tags import HTML, escape, literal 
from formbuild.helpers import field, checkbox_group, radio_group, start_form, end_form, start_layout, end_layout, start_with_layout, end_with_layout

class LayoutHelpers:
    def start(self, *k, **p):
        return start_form( *k, **p)

    def end(self, *k, **p):
        return end_form(*k, **p)

    def start_layout(self, *k, **p):
        return start_layout(*k, **p)

    def end_layout(self, *k, **p):
        return end_layout(*k, **p)

    def start_with_layout(self, *k, **p):
        return start_with_layout(*k, **p)

    def end_with_layout(self, *k, **p):
        return end_with_layout(*k, **p)

    def action_bar(self, fields):
        return literal('<tr><td colspan="3" align="right">')+literal('').join(fields)+literal('</td></tr>')

class FieldHelper:
    def field(self, **p):
        if not p.has_key('field'):
            p['field'] = u''
        else:
            p = p.copy()
            field_args = p['field'].copy()
            for arg in ['name', 'type']:
                if not field_args.has_key(arg):
                    raise Exception('No %r key passed in the "field" argument'%arg)
            type = field_args['type']
            del field_args['type']
            name = field_args['name']
            if not hasattr(self, type):
                raise Exception('No such field %r associated with this form'%type)
            value = field_args.get('value')
            if value is None:
                value = field_args.get('default')
                if self.values.has_key(name):
                    value = self.values.get(name)
            if field_args.has_key('default'):
                del field_args['default']
            if field_args.has_key('default_'):
               field_args['default'] = field_args['default_']
               del field_args['default_']
            field_args['value'] = value
            p['field'] = getattr(self, type)(**field_args)
            if self.errors.has_key(name):
                p['error'] = self.errors.get(name)
            return field(**p)

class BaseForm:
    def __init__(self, values=None, errors=None, state=None):
        self.values = values
        self.errors = errors
        self.state = state 
        if values is None:
            self.values = {}
        if errors is None:
            self.errors = {}

class SingleValueFields:

    def file(self, name, value=None, id=None, **options):
        if value is None:
            value = self.values.get(name)
        return file(name, value=value, id=id, **options)
    
    def password(self, name="password", value=None, id=None, **options):
        """Creates a password field
           Takes the same options as text"""
        if value is None:
            value = self.values.get(name)
        return password(name, value, id=id, **options)
        
    def textarea(self, name, value=None, id=None, rows=3, cols=16, **options):
        """Creates a text input area"""
        if value is None:
            value = self.values.get(name)
        return textarea(name, content=value, id=id, rows=rows, cols=cols, **options)
    
    def checkbox(self, name, value=None, checked=False, id=None, **options):
        """Creates a check box."""
        if value is None:
            value = self.values.get(name)
        if value == 'on':
            checked=True
        return checkbox(name, value=value, checked=checked, id=id, **options)
    
    def radio(self, name, value, checked=False, id=None, **options):
        """Creates a radio button."""
        return radio(name, value, checked, id=id, **options)
    
    def submit(self, name='commit', value="", id=None, **options):
        """\
        Creates a submit button with the text ``<tt>value</tt>`` as the 
        caption.
        """
        if value is None:
            value = self.values.get(name)
        return submit(value=value, name=name, id=id, **options)

    def dropdown(self, name, options, value=None, id=None, **attrs):
        if value is None:
            value = self.values.get(name)
        return select(name, selected_values=[value], options=options, id=id, **attrs)
        
    def text(self, name, value=None, id=None, **options):
        if value is None:
            value = self.values.get(name)
        return text(name, value, id=id, **options)
    
    def hidden(self, name, value=None, id=None, **options):
        if value is None:
            value = self.values.get(name)
        return hidden(name, value, id=id, **options)
    
    def radio_group(self, name, options, value=None, align='horiz', cols=4):
        if value is None:
            value = self.values.get(name)
        if value is None:
            selected_values = []
        else:
            selected_values = [value]
        return radio_group(name, value=selected_values, options=options, align=align, cols=cols)
    #
    # Deprecated Methods
    #

    def text_area(self, name, value=None, id=None, **options):
        warnings.warn(
            "text_area() is deprecated, use textarea() instead",
            DeprecationWarning, stacklevel=2
        )
        return self.textarea(name, value=value, id=id, **options)

    def check_box(self, name, value=None, id=None, **options):
        warnings.warn(
            "check_box() is deprecated, use checkbox() instead",
            DeprecationWarning, stacklevel=2
        )
        return self.checkbox(name, value=value, id=id, **options)

    def radio_button(self, name, value=None, id=None, **options):
        warnings.warn(
            "radio_button() is deprecated, use radio() instead",
            DeprecationWarning, stacklevel=2
        )
        return self.radio(name, value=value, id=id, **options)

    def date(self, *k, **p):
        warnings.warn(
            "date() is deprecated, use text() instead, they are the same",
            DeprecationWarning, stacklevel=2
        )
        return self.text(*k, **p)
        
    def static(self, name, value=None):
        warnings.warn(
            "radio_button() is deprecated, use radio() instead",
            DeprecationWarning, stacklevel=2
        )
        if value is None:
            value = self.values.get(name)
        return str(value)
        
    #
    # Removed
    #

    def select(self, name, option_tags='', id=None, **options):
        raise Exception('select() has been deprecated for over a year and is now removed. Please use dropdown() or combo() instead')
        # XXX Should distinguish between single and combo and take different values
        warnings.warn(
            "formbuild.builder.field.basic.select has been deprecated; please "
            "use formbuild.builder.field.basic.dropdown instead.",
            DeprecationWarning, 2
        )
        return select(name, option_tags, id=id, **options)

    def options(self, options, selected_values):
        raise Exception('options() has been removed because dropdown() now generates the values safely itself')
        warnings.warn(
            "options() is deprecated, options are generated automatically now and don't need to be passed to other methods explicitly",
            DeprecationWarning, stacklevel=2
        )
        o = ''
        for op in options:
            o += self.option(op, selected_values)+'\n'
        return o

class MultipleValueFields:

    def combo(self, name, options, selected_values=None, id=None, size=4, **attrs):
        if selected_values is None:
            selected_values = self.values.get(name)
        return select(name, selected_values=selected_values, options=options, size=size, multiple=True, id=id, **attrs)

    def checkbox_group(self, name, options, selected_values=None, align='horiz', cols=4):
        if selected_values is None:
            selected_values = self.values.get(name)
        return checkbox_group(name, selected_values=selected_values, options=options, align=align, cols=cols)


class Form(BaseForm, FieldHelper, LayoutHelpers, SingleValueFields, MultipleValueFields):
    pass



