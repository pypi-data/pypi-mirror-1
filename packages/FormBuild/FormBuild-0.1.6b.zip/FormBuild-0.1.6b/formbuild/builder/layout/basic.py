from formbuild.builder.layout import LayoutBuilder

class HtmlLayout(LayoutBuilder):

    type = 'formbuild.builder.layout.basic.HtmlFields'

    def simple_start(self):
        return '<table border="0">\n'
        
    def simple_end(self):
        return '</table>'

    def entry_start(self, name='', error=''):
        if name:
            name+= ':'
        return """<tr>
    <td valign="top">%s</td>
    <td>"""%(name)
    
    def entry_end(self, name='', error='' ):
        return """</td>
    <td valign="top">%s</td>
</tr>\n"""%(error)

    
class CssLayout(LayoutBuilder):
    
    type = 'formbuild.builder.layout.basic.CssFields'

    def __init__(self, css_prepend=''):
        if css_prepend:
            css_prepend += '-'
        self.css_prepend = css_prepend
        # Don't need to call LayoutBuilder.__init__()

    def simple_start(self):
        return ''
        
    def simple_end(self):
        return '<br class="%sform-helper-css-clear" />'%self.css_prepend

    def entry_start(self, name='', error=''):
        ouptut = ''
        if not name:
            name = '&nbsp;'
        else:
            name += ':'
        return '<div class="%sform-helper-layout-css-entry-name">\n%s\n</div>\n'%(self.css_prepend,name)
    
    def entry_end(self, name='', error='' ):
        if not error:
            error = '&nbsp;'
        return """<div class="%sform-helper-layout-css-entry-error">
    %s
</div>\n"""%(self.css_prepend, error)

#~ if __name__ == '__main__':
    #~ from formbuild import Form
    #~ class MyForm(Form):
        #~ layouts = BasicHTML
    #~ f = MyForm()
    #~ print f.layout.simple (f.layout.entry(name="Name", error="No Error", content=f.field.text(name="name")))
