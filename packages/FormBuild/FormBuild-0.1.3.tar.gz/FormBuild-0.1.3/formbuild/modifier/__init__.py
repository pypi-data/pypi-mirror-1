import inspect

def capture_params(method, after=None):

    def f(params):
        return params
    if after == None:
        after = f

    def getValue(*k, **p):
        args, ks, ps, defaults = inspect.getargspec(method.im_func)
        final = {}
        # Which have no defaults
        nodefaults = []
        if defaults:
            nodefaults = args[1:-len(defaults)]
        
        # Out of these which are specified by params
        for key, value in p.items():
            if key in nodefaults:
                nodefaults.pop(nodefaults.index(key))
        # We are left with words with no defaults and no params, these should correspond to the keywords:
        if len(k) < len(nodefaults):
            raise TypeError('Required parameter %s not specified.'%(repr(nodefaults[len(k):len(k)+1][0])))
        elif len(k) > len(nodefaults):
            overridedefaults = defaults[:len(k)]
            names = args[-len(defaults):][:len(k)-len(nodefaults)]
            counter = 0
            for name in names:
                if name in p.keys():
                    raise TypeError('Keyword and named parameter specified for %s'%repr(name))
                else:
                    final[name] = k[len(k)-len(nodefaults):][counter]
            for i in range(len(nodefaults)):
                final[args[i+1]] = k[i]
        else:
            # Assuming all is well we now know the parameters, defaults and keywords
            for i in range(len(k)):
                final[args[i+1]] = k[i]
        # That's the keywords sorted, now for the params
        for key, value in p.items():
            final[key] = value
        return after(final)
    return getValue

class ModifierBase:
    pass

class Build(ModifierBase):
    """Just returns the params entered"""
    def __init__(self, *objects):
        self._fields = Combine(*objects)

    def __call__(self, form):
        self._fields(form)

    def __getattr__(self, name):  
        method = getattr(self._fields, name)
        return capture_params(method)

class Capture(ModifierBase):
    def __init__(self, *objects):
        self._fields = None
        self._fields = Combine(*objects)
        self.captured = []

    def __call__(self, form):
        self._fields(form)

    def __getattr__(self, name):  
        method = getattr(self._fields, name)
        def func(params):
            self.captured.append([method.im_class.type+'.'+name, params])
            return None #method(**params)
        return capture_params(getattr(self._fields, name), func)

class CaptureAndReturn(Capture):
    """
    Capture the parameters and return them
    """
    def __getattr__(self, name):  
        method = getattr(self._fields, name)
        def func(params):
            self.captured.append([method.im_class.type+'.'+name, params])
            return method(**params)
        return capture_params(getattr(self._fields, name), func)

class Combine(ModifierBase):
    def __init__(self, *objects):
        self._objects = objects
        self.names = ''
        for object in self.__dict__['_objects']:
            self.names += object.__class__.__name__ + ', '
        if self.names:
            self.names = self.names[:-2]

    def __call__(self, form):
        self.form = form
        in_objects = []
        for object in self.__dict__['_objects']:
            in_objects.append(object(form))
        #self.__dict__['_objects'] = in_objects

    def __getattr__(self, name):
        for object in self.__dict__['_objects']:
            if hasattr(object, name):
                return getattr(object, name)
        raise AttributeError('Method %s could not be found in any of the combined classes %s'%(repr(name), self.names))

class Frozen(ModifierBase):    
    def __init__(self, *objects):
        self._fields = Combine(*objects)

    def __call__(self, form):
        self._fields(form)

    def __getattr__(self, name):        
        # We only want the value from the method, not the rest
        def func(params):
            value = None
            if params.has_key('value'):
                value = params['value']
            else:
                value = self._fields.form.get_default(params['name'])
            if value == None:
                return ''
            else:
                return str(value)
        return capture_params(getattr(self._fields, name), func)
