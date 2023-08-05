"""FormBuild - Helpful tools to generate HTML forms, designed to complement FormEncode

(C) James Gardner 2005 MIT Licence see FormBuild.__copyright__"""

__docformat__ = "restructuredtext"
from formbuild.form import Form
__copyright__ = """
Copyright (c) 2005 James Gardner <python@jimmyg.org>

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. The name of the author or contributors may not be used to endorse or
   promote products derived from this software without specific prior
   written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

def handle(schema, template, form=None, data=None, params=None, context=None, render_response=None, fragment=False):
    if data == None:
        data = {}
    else:
        if not isinstance(data, dict):
            raise TypeError('Expected data to be a dictionary')
            #~ values = {}
            #~ for k in data.c.keys():
                #~ values[k] = getattr(data, k)
            #~ data = values
    import formencode
    if params == None:
        from pylons import request
        params = {}
        for k in request.params.keys():
            v = request.params.getall(k)
            if len(v) == 1:
                params[k] = v[0]
            else:
                params[k] = v
    if context == None:
        from pylons import c as context
    if not form:
        form = Form
    if not render_response:
        from pylons.templating import render_response
    c = context
    errors = {}
    data.update(params)
    results=data
    if len(params):
        try:
            results = schema.to_python(results, state=c)
        except formencode.Invalid, e:
            errors = e.error_dict or {}
    c.form = form(results, errors)
    if not len(params) or errors:
        return results, errors, render_response(template, fragment=fragment)
    return results, errors, ''

"""

    # Some new thoughts for a better handle()

    import formbuild
    import formencode

    # in a controller
       
        
        def email_form(self):


            if len(request.params):
                try:
                    results = schema.to_python(results, state=c)
                except formencode.Invalid, e:
                    errors = e.error_dict or {}
                    results = e.values
                    c.form = form(dict(request.params), errors)
                    return submitted, results, errors, render_response(template, fragment=fragment)
                else:
                    c.form = form(results, {})
                    return results, {}, None
            else:
                return {}, {}, render_response(template, fragment=fragment)



 
        class ProcessedForm:
            def __init__(self, defaults={}, submitted={}, results={}, response={}, errors={}):
                self.submitted=submitted
                self.defaults=defaults
                self.results = results
                self.response = response
                self.errors = errors
                self.valid = False
                if not self.response:
                    self.valid = True
        
        def pylons_render_form(template, form, **options):
            fragment = options.get('fragment', False)
            from pylons.templating import render_response
            from pylons import c
            c.form = form
            return render_response(template, fragment=fragment)
            
            
        def handle(schema, template, form=None, defaults={}, submitted={}, render_from=pylons_render_form, render_options={}):
            defaults.update(submitted)
"""

