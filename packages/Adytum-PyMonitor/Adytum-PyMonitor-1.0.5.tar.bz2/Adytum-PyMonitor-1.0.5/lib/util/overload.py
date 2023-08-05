'''
I first came across this code by Lenard Lindstrom <len-l@telus.net> posted 
to comp.lang.python here:

  http://groups.google.com/groups?threadm=tyfekkoeyk2.fsf@pcepsft001.cern.ch

'''
import sys

class OverloadedFunction(object):
    class BoundMethod:
        def __init__(self, functions, instance, owner):
            self.bm_functions = functions
            self.bm_instance = instance
            self.bm_owner = owner
        def __getitem__(self, index):
            return self.bm_functions[index].__get__(self.bm_instance,
                self.bm_owner)
        def __call__(self, *args, **kwargs):
            for index in range(0,len(self.bm_functions)):
                #try:
                func = self.__getitem__(index) 
                return func(args, kwargs)
                #except: pass
                     
    def __init__(self, functions):
        self.of_functions = functions
    def __get__(self, instance, owner):
        return self.BoundMethod(self.of_functions,
                                instance,
                                owner)

def overloaded(func):

    '''
    # Test case:
    >>> class blob:
    ...     def __init__(self, member):
    ...         self.member = member
    ...     def f(self):
    ...         return "f 0: member=%s" % self.member
    ...     f = overloaded(f)
    ...     def f(self, s):
    ...         return "f 1: member=%s, s=%s" % (self.member, s)
    ...     f = overloaded(f)

    >>> b=blob("XXX")
    >>> print b.f[0]()
    f 0: member=XXX
    >>> print b.f[1]("Yet another f")
    f 1: member=XXX, s=Yet another f
    >>> print b.f()
    >>> print b.f('test')
    '''

    listattr = '_%s_functions_' % func.__name__
    attrs = sys._getframe(1).f_locals
    try:
        functions = attrs[listattr]
        functions.append(func)
    except KeyError:
        functions = [func]
        attrs[listattr] = functions
    return OverloadedFunction(functions)

def _test():
    import doctest, overload
    return doctest.testmod(overload)

if __name__ == '__main__':
    _test()
