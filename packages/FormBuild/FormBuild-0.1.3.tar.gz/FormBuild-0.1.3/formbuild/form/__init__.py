from formbuild.modifier import Combine
from formbuild.builder.field.basic import HtmlFields
from formbuild.builder.layout.basic import HtmlLayout

class FormBase:
    """
    All ``Form`` classes have the following attributes:
        
    field
        Generate a field object
        
    layout
        Tools for rendering fields and text into pages, sections, questions and sub questions
    """
    def __init__(self, defaults=[{}], errors=[{}] ):
        """
        The following attributes are used:
        
        defaults
            This is a list of dictionaries. When looking for a default value the list is traveresed and the first value where the key matches the name of the field is used as the default.
        
        errors
            This is a list of dictionaries. It is searched in the same way as ``defaults`` and the first matching value is used as the error message associated with the field.
        """
        #raise Exception('sdf')

        if isinstance(defaults, dict):
            defaults = [defaults]
        else:
            if not isinstance(defaults, list):
                raise Exception('Invalid defaults, expected dictionary or list of dictionaries, not %s'%repr(defaults))
        for default_set in defaults:
            if not isinstance(default_set, dict):
                raise Exception('Invalid defaults, expected dictionary or list of dictionaries, not %s'%repr(defaults))
        self.defaults = defaults
        if isinstance(errors, dict):
            errors = [errors]
        else:
            if not isinstance(errors, list):
                raise Exception('Invalid errors, expected dictionary or list of dictionaries, not %s'%repr(errors))
        for error_set in errors:
            if not isinstance(error_set, dict):
                raise Exception('Invalid errors, expected dictionary or list of dictionaries, not %s'%repr(errors))
        self.errors = errors

        builder_attributes = []
        for k in dir(self):
            if k not in ['__doc__','defaults','errors', '__init__', '__module__', 'addField', 'as_hidden', 'end', 'getDefault', 'getError', 'getField', 'ifError', 'start']:
                builder_attributes.append(k)

        for attribute in builder_attributes:
            a = getattr(self, attribute)
            if isinstance(a, tuple) or isinstance(a, list):
                setattr(self, attribute, Combine(*a))
            
            getattr(self, attribute)(self)

    def if_error(self, name, if_="", else_=""):
        for errors in self.errors:
            if errors.has_key(name):
                if if_ == '':
                    return errors[name]
                else:
                    return if_
                break
        return else_
            
    def get_error(self, name, default='', format=None):
        #raise Exception(self.errors)
        e = None
        for errors in self.errors:
            if errors.has_key(name):
                e = errors[name]
                break
        if e == None:
            e = default
        if format != None:
            e = format%e
        return e

    def start(self, **p):
        s = ''
        for k,v in p.items():
            s+='%s="%s" '%(k,v)
        return '<form %s>'%s
    
    def end(self):
        return '</form>'

    #~ def addField(self, field_type, **field_params):
        #~ f = {}
        #~ for k, v in field_params.items():
            #~ f[k]=v
        #~ f['type'] = field_type
        #~ self.field_data.append(f)
    
    #~ def getField(self, name):
        #~ return self.field_data[name]

    def get_default(self, name, default=None):
        if type(self.defaults) <> type([]):
            raise Exception(self.defaults)
            
        for d in self.defaults:
            if d.has_key(name):
                return d[name]
        return default
    
    def as_hidden(self, params):
        f = ''
        for k,v in params.items():
            f += self.field.hidden(name=k, value=v)
        return f

class Form(FormBase):
    field = HtmlFields()
    layout = HtmlLayout()

