# -*- coding: utf-8 -*-

"""\

FormBuild 2.0 is a complete re-write of FormBuild 0.1 with a vastly simplified
API focusing on the core use case and with automatic variable escaping< built in
to help prevent XSS attacks. The new API supports all the features of the old
one but is easier to understand.

"""

import warnings
from formbuild import helpers
import webhelpers.html.tags
from webhelpers.html.builder import HTML, literal 

# Deprecated but needed for backwards compatibility with the Pylons Book.
from formbuild.helpers import *
from webhelpers.html.tags import *

import logging
log = logging.getLogger(__name__)

class LayoutHelpers:

    def __init__(self, table_class='formbuild'):
        self.table_class = table_class

    def start(self, url, method="post", multipart=False, **attrs):
        return helpers.start_form(url, method, multipart, **attrs)
    start.__doc__ = helpers.start_form.__doc__

    def end(self):
        return end_form()
    end.__doc__ = helpers.end_form.__doc__

    def start_layout(self, table_class=None):
        return helpers.start_layout(table_class or self.table_class)
    start_layout.__doc__ = helpers.start_layout.__doc__

    def end_layout(self):
        return helpers.end_layout()
    end_layout.__doc__ = helpers.end_layout.__doc__

    def start_with_layout(self, url, method="post", multipart=False, table_class=None, **attrs):
        return helpers.start_with_layout(url, method, multipart, table_class or self.table_class, **attrs)
    start_with_layout.__doc__ = helpers.start_with_layout.__doc__

    def end_with_layout(self):
        return helpers.end_with_layout()
    end_with_layout.__doc__ = helpers.end_with_layout.__doc__

    def action_bar(self, fields):
        """\
        Generate an action bar containing submit buttons from the list of fields
        """
        return literal('<tr><td></td><td colspan="2">')+literal('').join(fields)+literal('</td></tr>')

class FieldHelper:
    def field(
        self,
        label='', 
        field='',
        required=False, 
        label_desc='', 
        field_desc='',
        help='',
        error='',
        name=None,
    ):
        """\
	Generate a field row in the form but use the dictionary of arguments
        passed as the ``field`` argument to build the field itself, replacing the field
        value and the error message as appropriate.

        The following will be checked in order of preference when determining the value to
        use:

        1. The value corresponding to a ``value`` key in the dictionary passed as the ``field`` argument.
        2. A suitable value passed as an argument to the constructor as the ``defualts`` argument
        3. The value corresponding to a ``default`` key in the dictionary passed as the ``field`` argument.
        For choosing error messages, the ``error`` argument passed as an argument to this method is used if it exists, otherwise any error message passed to the class itself is used. 
        """
        if isinstance(field, dict):
            for arg in ['name', 'type']:
                if not field.has_key(arg):
                    raise Exception('No %r key passed in the "field" argument'%arg)
            type = field['type']
            del field['type']
            if not hasattr(self, type):
                raise Exception('No such field %r associated with this form'%type)
            name = field['name']
            value = None
            if field.has_key('value'):
                value = field['value']
            elif self.values.has_key(name):
                value = self.values.get(name)
            elif field.has_key('default'):
                value = field['default']
                del field['default']
            field['value'] = value
            field_html = getattr(self, type)(**field)
            error_html = error or self.errors.get(name)
        else:
            # Handling it explicitly with no errors:
            # XXX Should raise a warning?
            field_html = field
            error_html = error or self.errors.get(name)
        return helpers.field(
            label=label, 
            field=field_html,
            required=required, 
            label_desc=label_desc, 
            field_desc=field_desc,
            help=help,
            error=error_html
        )
        
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
    """\
    These are methods which represent helpers which take single value arguments. When called
    directly they will take the ``value`` argument passed to them or the default from the Form
    class constructor.
    """

    def file(self, name, value=None, id=None, **options):
        if value is None:
            value = self.values.get(name)
        return webhelpers.html.tags.file(name, value=value, id=id, **options)
    
    def password(self, name="password", value=None, id=None, **options):
        """Creates a password field
           Takes the same options as text"""
        if value is None:
            value = self.values.get(name)
        return webhelpers.html.tags.password(name, value, id=id, **options)
        
    def textarea(self, name, value=None, id=None, rows=3, cols=16, **options):
        """Creates a text input area"""
        if value is None:
            value = self.values.get(name)
        return webhelpers.html.tags.textarea(name, content=value, id=id, rows=rows, cols=cols, **options)
    
    def checkbox(self, name, value=None, checked=False, id=None, **options):
        """Creates a check box."""
        if value is None:
            value = self.values.get(name)
        if value == 'on':
            checked=True
        return webhelpers.html.tags.checkbox(name, value=value, checked=checked, id=id, **options)
    
    def radio(self, name, value, checked=False, id=None, **options):
        """Creates a radio button."""
        return webhelpers.html.tags.radio(name, value, checked, id=id, **options)
    
    def submit(self, name='commit', value="", id=None, **options):
        """\
        Creates a submit button with the text ``<tt>value</tt>`` as the 
        caption.
        """
        if value is None:
            value = self.values.get(name)
        return webhelpers.html.tags.submit(value=value, name=name, id=id, **options)

    def dropdown(self, name, options, value=None, id=None, **attrs):
        if value is None:
            value = self.values.get(name)
        return webhelpers.html.tags.select(name, selected_values=[value], options=options, id=id, **attrs)
        
    def text(self, name, value=None, id=None, **options):
        if value is None:
            value = self.values.get(name)
        return webhelpers.html.tags.text(name, value, id=id, **options)
    
    def hidden(self, name, value=None, id=None, **options):
        if value is None:
            value = self.values.get(name)
        return webhelpers.html.tags.hidden(name, value, id=id, **options)
    
    def radio_group(self, name, options, value=None, align='horiz', cols=4):
        if value is None:
            value = self.values.get(name)
        if value is None:
            selected_values = []
        else:
            selected_values = [value]
        return helpers.radio_group(name, value=selected_values, options=options, align=align, cols=cols)
    def static(self, name, value=None):
        """
        Return the static value instead of an HTML field.
        """
        if value is None:
            value = self.values.get(name)
        return str(value)

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
    """\
    These are methods which represent helpers which take multiple value arguments. When called
    directly they will take the ``value`` argument passed to them or the default from the Form
    class constructor.
    """
    def combo(self, name, options, selected_values=None, id=None, size=4, **attrs):
        if selected_values is None:
            selected_values = self.values.get(name)
        return webhelpers.html.tags.select(name, selected_values=selected_values, options=options, size=size, multiple=True, id=id, **attrs)

    def checkbox_group(self, name, options, selected_values=None, align='horiz', cols=4):
        if selected_values is None:
            selected_values = self.values.get(name)
        return checkbox_group(name, selected_values=selected_values, options=options, align=align, cols=cols)

    def radio_group(self, name, options, selected_values=None, align='horiz', cols=4):
        if selected_values is None:
            selected_values = self.values.get(name)
        return radio_group(name, selected_values=selected_values, options=options, align=align, cols=cols)

class Form(BaseForm, FieldHelper, LayoutHelpers, SingleValueFields, MultipleValueFields):
    def __init__(self, values=None, errors=None, state=None, table_class='formbuild'):
        BaseForm.__init__(self, values, errors, state)
        LayoutHelpers.__init__(self, table_class)

#def handle(schema, template, form=None, data=None, params=None, context=None, render_response=None, fragment=False):
#    if data == None:
#        data = {}
#    else:
#        if not isinstance(data, dict):
#            raise TypeError('Expected data to be a dictionary')
#            #~ values = {}
#            #~ for k in data.c.keys():
#                #~ values[k] = getattr(data, k)
#            #~ data = values
#    import formencode
#    if params == None:
#        from pylons import request
#        params = {}
#        for k in request.params.keys():
#            v = request.params.getall(k)
#            if len(v) == 1:
#                params[k] = v[0]
#            else:
#                params[k] = v
#    if context == None:
#        from pylons import c as context
#    if not form:
#        form = Form
#    if not render_response:
#        from pylons.templating import render_response
#    c = context
#    errors = {}
#    data.update(params)
#    results=data
#    if len(params):
#        try:
#            results = schema.to_python(results, state=c)
#        except formencode.Invalid, e:
#            errors = e.error_dict or {}
#    c.form = form(results, errors)
#    if not len(params) or errors:
#        return results, errors, render_response(template, fragment=fragment)
#    return results, errors, ''

def errors_to_dict(exception):
    log.info('Converting errors %r', exception)
    return exception.unpack_errors() or {}

def params_to_dict(params):
    result = {}
    for k in params.keys():
        v = params.getall(k)
        if len(v) == 1:
            result[k] = v[0]
        else:
            result[k] = v
    return dict(result)

class FormEncodeState(object):
    pass

class ValidationState(object):
    def __init__(self, state=None, key='validation'):
        if state is not None:
            self.__dict__['_state'] = state
        self.__dict__['_formencode_state'] = FormEncodeState()

    def __setattr__(self, name, value):
        if name in ['full_dict', 'key']:
            setattr(self.__dict__['_formencode_state'], name, value)
        else:
            setattr(self.__dict__['_state'], name, value)
    
    def __getattr__(self, name):
        if name in ['full_dict', 'key']:
            return getattr(self.__dict__['_formencode_state'], name)
        else:
            return getattr(self.__dict__['_state'], name)
