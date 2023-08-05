from formbuild.builder.field import FieldsBuilder

class HtmlFields(FieldsBuilder):
    
    type = 'formbuild.builder.field.compound.HtmlFields'

    # from pythonweb.org web.form
    def radio_group(self, name, options, value=None, align='horiz', cols=4):
        """Radio Group Field."""
        if value == None:
            value = self._form.get_default(name)
        output=''
        if len(options)>0:
            if align <> 'table':
                for option in options:
                    checked=''
                    align=''
                    if not isinstance(option, list) and not isinstance(option, tuple):
                        k = option
                        v = option
                    else:
                        k=option[1]
                        v=option[0]
                    if str(v)==str(value):
                        checked=" checked"
                    if align == 'vert':
                        align='<br>'
                    output+='<input type="radio" name="%s" value="%s"%s />%s%s\n'%(name, v, checked, k,align)
                #output = output[2:]
            else:
                output += '\n\n    <table border="0" width="100%" cellpadding="0" cellspacing="0">\n    <tr>\n'
                counter = -1
                for option in options:
                    counter += 1
                    if ((counter % cols) == 0) and (counter <> 0):
                        output += '    </tr>\n    <tr>\n'
                    output += '      <td>'
                    checked=''
                    align=''
                    if not isinstance(option, list) and not isinstance(option, tuple):
                        k = option
                        v = option
                    else:
                        k=option[1]
                        v=option[0]
                    if str(v)==str(value):
                        checked=" checked"
                    
                    output += '<input type="radio" name="%s" value="%s"%s />%s%s'%(name, v, checked, k,align)
                    output += '</td>\n      <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>\n'
                    
                counter += 1
                while (counter % cols):
                    counter += 1
                    output += '      <td></td>\n      <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>\n'
                output += '    </tr>\n    </table>\n\n'
        return output

    def check_box_group(self, name, options, values=None, align='vert', cols=4):
        """Check Box Group Field."""
        if values == None:
            values = self._form.get_default(name)
        if not isinstance(values, list) and not isinstance(values, tuple):
            values = [values]
        output = ''
        if len(options) > 0:
            if align <> 'table':
                for option in options:
                    if not isinstance(option, list) and not isinstance(option, tuple):
                        k = option
                        v = option
                    else:
                        k=option[1]
                        v=option[0]
                    checked=''
                    align=''
                    if v in values:
                        checked=" checked"
                    if align == 'vert':
                        align='<br>'
                    output+='<input type="checkbox" name="%s" value="%s"%s />%s%s\n'%(name, v, checked, k,align)
            else:
                output += '\n\n    <table border="0" width="100%" cellpadding="0" cellspacing="0">\n    <tr>\n'
                counter = -1
                for option in options:
                    counter += 1
                    if ((counter % cols) == 0) and (counter <> 0):
                        output += '    </tr>\n    <tr>\n'
                    output += '      <td>'
                    checked=''
                    align=''
                    if not isinstance(option, list) and not isinstance(option, tuple):
                        k = option
                        v = option
                    else:
                        k=option[1]
                        v=option[0]
                    if v in default:
                        checked=" checked"
                    output += '<input type="checkbox" name="%s" value="%s"%s />%s%s'%(name, v, checked, k,align)
                    output += '</td>\n      <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>\n'
                    
                counter += 1
                while (counter % cols):
                    counter += 1
                    output += '      <td></td>\n      <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>\n'
                output += '    </tr>\n    </table>\n'
        return output[:-1]
