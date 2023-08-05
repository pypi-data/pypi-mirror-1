from formbuild.builder.field import FieldsBuilder
from webhelpers.rails.form_tag import *
import datetime
import warnings

class HtmlFields(FieldsBuilder):

    type = 'formbuild.builder.field.basic.HtmlFields'
    
    def date(self, *k, **p):
        return self.text(*k, **p)
        
    def static(self, name, value=None):
        if value == None:
            value = self._form.get_default(name)
        return str(value)
        
    # Straight from pylons.helpers with different names and with no defaults
    
    def dropdown(self, name, values, value=None, id=None, **options):
        if value == None:
            value = self._form.get_default(name)
        #raise Exception(value)
        op = self.options(values, selected_values = value)
        return select(name, op, id=id, **options)

    def date(self, name, year_start, year_end=None, title="Choose a date", **options):
        """Experimental JavaScript date field based on developer.yahoo.com/yui date widget. Not yet complete.
        
        Although this works if you include the Yahoo components necessary for the date examples in Yahoo's documentation it isn't the cleanest
        way of doing it so it will probably be re-written in the future.
        """
        if year_end == None:
            year_end = datetime.datetime.now().year
        lines = []
        if 1:
              lines.append('''<script language="javascript">
    YAHOO.namespace("example.calendar");

    function init''')
              lines.append( name )
              # SOURCE LINE 9
              lines.append('''() {
        this.today = new Date();
        var thisMonth = this.today.getMonth();
        var thisDay = this.today.getDate();
        var thisYear = this.today.getFullYear();
        this.link''')
              lines.append( name )
              lines.append(''' = document.getElementById(\'dateLink''')
              lines.append( name )
              # SOURCE LINE 10
              lines.append('''\');
        this.''')
              lines.append( name )
              lines.append(''' = document.getElementById(\'''')
              lines.append( name )
              # SOURCE LINE 11
              lines.append('''\');
        this.selMonth''')
              lines.append( name )
              lines.append(''' = document.getElementById(\'selMonth''')
              lines.append( name )
              # SOURCE LINE 12
              lines.append('''\');
        this.selDay''')
              lines.append( name )
              lines.append(''' = document.getElementById(\'selDay''')
              lines.append( name )
              # SOURCE LINE 13
              lines.append('''\');
        this.selYear''')
              lines.append( name )
              lines.append(''' = document.getElementById(\'selYear''')
              lines.append( name )
              # SOURCE LINE 14
              lines.append('''\');
        YAHOO.example.calendar.cal''')
              lines.append( name )
              lines.append(''' = new YAHOO.widget.Calendar2up("YAHOO.example.calendar.cal''')
              lines.append( name )
              lines.append('''","container''')
              lines.append( name )
              lines.append('''",(this.selMonth''')
              lines.append( name )
              lines.append('''.value)+"/"+(this.selYear''')
              lines.append( name )
              lines.append('''.value),(this.selMonth''')
              lines.append( name )
              lines.append('''.value)+"/"+this.selDay''')
              lines.append( name )
              lines.append('''.value+"/"+(this.selYear''')
              lines.append( name )
              # SOURCE LINE 15
              lines.append('''.value));
        YAHOO.example.calendar.cal''')
              lines.append( name )
              lines.append('''.title = "''')
              lines.append( title )
              # SOURCE LINE 16
              lines.append('''";
        YAHOO.example.calendar.cal''')
              lines.append( name )
              lines.append('''.setChildFunction("onSelect",setDate''')
              lines.append( name )
              # SOURCE LINE 17
              lines.append(''');
        YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 20
              lines.append('''.render();
    }

    function showCalendar''')
              lines.append( name )
              # SOURCE LINE 21
              lines.append('''() {			
        var pos = YAHOO.util.Dom.getXY(link''')
              lines.append( name )
              # SOURCE LINE 22
              lines.append(''');
        YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 23
              lines.append('''.outerContainer.style.display=\'block\';
        YAHOO.util.Dom.setXY(YAHOO.example.calendar.cal''')
              lines.append( name )
              lines.append('''.outerContainer, [pos[0],pos[1]+link''')
              lines.append( name )
              # SOURCE LINE 26
              lines.append('''.offsetHeight+1]);
    }

    function setDate''')
              lines.append( name )
              # SOURCE LINE 27
              lines.append('''() {
        var date''')
              lines.append( name )
              lines.append(''' = YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 28
              lines.append('''.getSelectedDates()[0];
        selMonth''')
              lines.append( name )
              lines.append('''.selectedIndex=date''')
              lines.append( name )
              # SOURCE LINE 29
              lines.append('''.getMonth();
        selDay''')
              lines.append( name )
              lines.append('''.selectedIndex=date''')
              lines.append( name )
              # SOURCE LINE 30
              lines.append('''.getDate()-1;
        selYear''')
              lines.append( name )
              lines.append('''.selectedIndex=date''')
              lines.append( name )
              lines.append('''.getFullYear()-''')
              lines.append( year_start )
              # SOURCE LINE 31
              lines.append(''';
        YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 32
              lines.append('''.hide();
        document.getElementById(\'''')
              lines.append( name )
              lines.append('''\').value = date''')
              lines.append( name )
              lines.append('''.getFullYear()+\'-\'+(date''')
              lines.append( name )
              lines.append('''.getMonth()+1)+\'-\'+date''')
              lines.append( name )
              # SOURCE LINE 33
              lines.append('''.getDate();
        //alert(document.getElementById(\'''')
              lines.append( name )
              # SOURCE LINE 36
              lines.append('''\').value)
    }

    function changeDate''')
              lines.append( name )
              # SOURCE LINE 37
              lines.append('''() {
        var month = this.selMonth''')
              lines.append( name )
              # SOURCE LINE 38
              lines.append('''.selectedIndex;
        var day = this.selDay''')
              lines.append( name )
              # SOURCE LINE 39
              lines.append('''.selectedIndex + 1;
        var year = this.selYear''')
              lines.append( name )
              lines.append('''.selectedIndex + ''')
              lines.append( year_start )
              # SOURCE LINE 40
              lines.append(''';
        YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 41
              lines.append('''.select((month+1) + "/" + day + "/" + year);
        YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 42
              lines.append('''.setMonth(month);
        YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 43
              lines.append('''.setYear(year);
        YAHOO.example.calendar.cal''')
              lines.append( name )
              # SOURCE LINE 44
              lines.append('''.render();
        document.getElementById(\'''')
              lines.append( name )
              # SOURCE LINE 45
              lines.append('''\').value = year+\'-\'+(month+1)+\'-\'+day
        //alert(document.getElementById(\'''')
              lines.append( name )
              # SOURCE LINE 48
              lines.append('''\').value)
    }

    YAHOO.util.Event.addListener(window, "load", init''')
              lines.append( name )
              day = 1
              month = 1
              year = year_start
              if self._form.get_default(name):
                    if isinstance(self._form.get_default(name), str):
                        if len(self._form.get_default(name).split('-'))==3:
                            day = self._form.get_default(name).split('-')[2]
                            month = self._form.get_default(name).split('-')[1]
                            year = self._form.get_default(name).split('-')[0]
                    else:
                        day = self._form.get_default(name).day
                        month = self._form.get_default(name).month
                        year = self._form.get_default(name).year

              # SOURCE LINE 51
              lines.append(''');		
</script>
<div>
''')
              lines.append( self.hidden(name=name, id=name, value="%s-%s-%s"%(year, month, day)) )
              # SOURCE LINE 56
              lines.append('''

''')
              lines.append( self.dropdown(
    'selDay'+name,
    [[x,x] for x in range(1,32)], 
     onchange="changeDate"+name+"()", id='selDay'+name, value=day )  )
              # SOURCE LINE 70
              lines.append(''' 
''')
              lines.append( self.dropdown('selMonth'+name,[
    ['1', 'Jan'],
    ['2', 'Feb'],
    ['3', 'Mar'],
    ['4', 'Apr'],
    ['5', 'May'],
    ['6', 'Jun'],
    ['7', 'Jul'],
    ['8', 'Aug'],
    ['9', 'Sep'],
    ['10', 'Oct'],
    ['11', 'Nov'],
    ['12', 'Dec'],
], onchange="changeDate"+name+"()", id='selMonth'+name, value=month ) )
              # SOURCE LINE 74
              lines.append(''' 
''')
              lines.append( self.dropdown(
        'selYear'+name,
        [[x,x] for x in range(year_start, year_end+1)], 
        onchange="changeDate"+name+"()", id='selYear'+name, value=year )  )
              # SOURCE LINE 76
              lines.append('''

<a href="javascript:void(null)" onclick="showCalendar''')
              lines.append( name )
              lines.append('''()"><img id="dateLink''')
              lines.append( name )
              # SOURCE LINE 78
              lines.append('''" src="/assets/calendar.png" border="0" style="vertical-align:middle;margin:5px" alt="choose" /></a>
</div>
<div id="container''')
              lines.append( name )
              lines.append('''" style="position:absolute;display:none"></div>

''')
              # END BLOCK body
        return ''.join([str(x) for x in lines])


    def select(self, name, option_tags='', id=None, **options):
        # XXX Should distinguish between single and combo and take different values
        warnings.warn(
            "formbuild.builder.field.basic.select has been deprecated; please "
            "use formbuild.builder.field.basic.dropdown instead.",
            DeprecationWarning, 2)
        return select(name, option_tags, id=id, **options)
        
    def options(self, options, selected_values):
        o = ''
        for op in options:
            o += self.option(op, selected_values)+'\n'
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
        if value == 'on':
            checked=True
        return check_box(name, value=value, checked=checked, id=id, **options)
    
    # XXX Should be radio group
    def radio(self, name, value, checked=False, id=None, **options):
        """Creates a radio button."""
        return radio_button(name, value, checked, id=id, **options)
    
    def submit(self, name='commit', value="", id=None, **options):
        """Creates a submit button with the text <tt>value</tt> as the caption."""
        if value == None:
            value = self._form.get_default(name)
        return submit(value=value, name=name, id=id, **options)
        
