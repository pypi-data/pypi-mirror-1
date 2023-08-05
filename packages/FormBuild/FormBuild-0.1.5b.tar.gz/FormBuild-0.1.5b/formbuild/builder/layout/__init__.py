
from formbuild.builder import Builder

class LayoutBuilder(Builder):
    """
    The base class of FormBuild extensions which change the behavious of form attribute methods.
    """

    def __call__(self, form):
        self.form = form

    def __getattr__(self, name, test=0):
        parts = dir(self.__class__)
        if name+'_end' in parts and name+'_start' in parts:
            def helper(content='', *k, **params):
                return getattr(self,name+'_start')(*k, **params) + content + getattr(self,name+'_end')(*k, **params)
            return helper
        else:
            raise AttributeError('No such method %s'%repr(name))
