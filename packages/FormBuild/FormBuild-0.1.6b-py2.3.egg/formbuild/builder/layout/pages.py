from formbuild.builder.layout import LayoutBuilder

# XXX Layout items should know where they are in the tree
"""For example warning() should know whether to format itself for sub_questions or questions"""

class HtmlLayout(LayoutBuilder):

    type = 'formbuild.builder.layout.pages.HtmlFields'

    def javascript_start(self):
        return """
<script langague="text/javascript">
function show(id){
    element = document.getElementById(id)
    element.style.visibility = 'visible'
}
function hide(id){
    element = document.getElementById(id)
    element.style.visibility = 'hidden'
}
</script>
"""
    def javascript_end(self):
        return ''

    # @@@ Page @@@
    def page_start(self, title='', description=''):
        return ("<h2>%s</h2>"%title)+description

    def page_end(self, name='', description='', title=''):
        return ''
    
    # @@@ Section @@@
    def section_start(self, title='', description='', ):
        return '<fieldset><legend><b>%(title)s</b></legend>%(description)s<table width="100%%" border="0">'%{
            'title':title,
            'description':description,
        }

    def section_end(self, name='', description='', title=''):
        return '</table></fieldset><br />'
    
    # @@@ Question @@@
    def question_start(self, name='', description='', title=''):
        return """<tr><td colspan="2">%s</td></tr>
            <tr><td>
                <table width="100%%" boder="0">"""%title
                
    def question_end(self, *k, **p):
        return """</table></td></tr>"""
        
    # @@@ Question Spacer @@@
    def question_spacer_start(self):
        return '<tr><td colspan="2"><hr /></td></tr>'
        
    def question_spacer_end(self):
        return ''
    
    # @@@ Sub Question Spacer @@@
    def sub_question_spacer_start(self):
        return '<tr><td colspan="3"><hr style="height: 1px" /></td></tr>'
        
    def sub_question_spacer_end(self):
        return ''

    # @@@ Sub Question @@@
    def sub_question_start(self, description='', title=''):
        return '<tr><td valign="top">%s</td><td valign="top">'%(title)

    def sub_question_end(self, *k, **p):
        return '</td></tr>'
        
    def field(self, label, name, type, **attributes):
        """Build a field with a label in a table row.
    
        type
          This can be any "blah" for which there exists a "blahField".
    
        """
        label = self.label(name, label)
        field = getattr(self, "%sField" % type)(name, **attributes)
        return '<tr valign="top"><td>%s</td><td>%s</td></tr>' % (label, field)
    
    def fieldset(self, fields):
        return '<fieldset>%s</fieldset>'%fields
    
    def label(self, content, label):
        return '<label for="%s">%s</label> %s'%(label,label, content)
    
    def focusField(self, form, field):
        """Output the JavaScript to focus a field.
    
        Use this to set the default focus of a form.  Call this *after* you
        have output the given field.
    
        form
          This is the name attribute of the ``<form>`` tag.
    
        field
          This is the name or ``id`` attribute of the field.
    
        """
       
        return """\
    <script type="text/javascript"><!--
    document.%s.%s.focus();
    // --></script>""" % (htmlent(form), htmlent(field))

    def question_warning_start(self):
        return '<tr><td colspan="2"><div style="background: #ffc; padding: 10px; border: 1px solid #ccc;">'
        
    def question_warning_end(self):
        return '</div></td></tr>'

    def question_note_start(self):
        return '<tr><td colspan="2"><div style="background: #eee; padding: 10px; border: 1px solid #ccc;">'
        
    def question_note_end(self):
        return '</div></td></tr>'
        
    def sub_question_warning_start(self):
        return self.question_warning_start()
        
    def sub_question_warning_end(self):
        return self.question_warning_end()

    def sub_question_note_start(self):
        return self.question_note_start()
        
    def sub_question_note_end(self):
        return self.question_note_end()
        
#~ if __name__ == '__main__':
    #~ r = Renderer()
    #~ print r.page('content', 'asd')
    #~ print r.page_start('asd')+'content'+r.page_end()
