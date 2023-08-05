"""
Forms expect the defaults to be either single values or lists of values. The values from ``cgi.FieldStorage()`` aren't quite suitable. 
# XXX Write a converter function
"""
from formbuild.builder import Builder

class FieldsBuilder(Builder):
    """
    The base class of all FormBuild extensions that add methods to a form attribute.
    """
  
    def __init__(self):
        self.type = 'fields'

    def __call__(self, form):
        self._form = form
    
    def _encode(self, s):
        translations = {"&": "&amp;", '"': "&quot;", "<": "&lt;", ">": "&gt;"}
        l = list(str(s))
        for i in range(len(l)):
            c = l[i]
            l[i] = translations.get(c, c)
        return "".join(l)
        
    # Deprecated
    def _attributes(self, attributes):
        output = ''
        for key in attributes.keys():
            output += ' %s="%s"' % (key, attributes[key]) 
        return output

    def option(self, option, selected_values):
        
        if isinstance(option, tuple) or isinstance(option, list):
            (value, label) = option
        else:
            (value, label) = (option, option)
        selected = ""
        if not (isinstance(selected_values, tuple) or isinstance(selected_values, list)):
            selected_values = [selected_values]
        for v in selected_values:
            if str(v) == str(value):
                selected = ' selected="selected"'
                break;
        return '<option value="%s"%s>%s</option>' % (value, selected, label)
       
    def options(self, options, selected_values):
        mode = 'value'
        if isinstance(options[0], tuple) or isinstance(options[0], list):
            mode = 'list'
        counter = 1
        result = ''
        for option in options:
            if mode=='list':
                (value, label) = counter, option
            else:
                (value, label) = option
            counter += 1
            selected = ""
            if not (isinstance(selected_values, tuple) or isinstance(selected_values, list)):
                selected_values = [selected_values]
            for v in selected_values:
                if str(v) == str(value):
                    selected = ' selected="selected"'
                    break;
            result += '<option value="%s"%s>%s</option>\n' % (value, selected, label)
        return result  
