
class CreatorBase:
    pass

class CaptureDataRecreator(CreatorBase):
    def __init__(self, form, init_params={}):
        self.form = form
        self.init_params = init_params

    def create(self, data):
        result = []

        for call, params in data:
            parts = call.split('.')
            module = '.'.join(parts[:-2])
            class_ = parts[-2]
            method = parts[-1]
            
            live = __import__(module, globals(), locals(), [class_]).__dict__[class_]
            if self.init_params.has_key('.'.join(parts[:-1])):
                p = self.init_params['.'.join(parts[:-1])]
            else:
                p = {}
            l = live(**p)
            l(self.form)
            #raise Exception(parts, module, class_, method)#, module_)
            #raise Exception(live)
            #live = from module import class_
            
            r = getattr(l, method)(**params)
            result.append(r)
        return result