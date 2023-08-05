'''
Title: Dependency Injection The Python Way
Submitter: Zoran Isailovski (other recipes)
Last Updated: 2005/05/05
Version no: 1.4
Category: OOP
Description: Sample Pythonic Inversion-of-Control Pseudo-Container.
Source: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/413268
'''

class FeatureBroker:
    '''

    '''
    def __init__(self, allowReplace=False):
        self.providers = {}
        self.allowReplace = allowReplace

    def provide(self, feature, provider, *args, **kwargs):
        if not self.allowReplace:
            assert not self.providers.has_key(feature), "Duplicate feature: %r" % feature
        if callable(provider):
            def call(): return provider(*args, **kwargs)
        else:
            def call(): return provider
        self.providers[feature] = call

    def __getitem__(self, feature):
        try:
            provider = self.providers[feature]
        except KeyError:
            raise KeyError, "Unknown feature named %r" % feature
        return provider()

features = FeatureBroker()

'''
Representation of Required Features and Feature Assertions

The following are some basic assertions to test the suitability of
injected features:
'''
def noAssertion(obj): 
    return True

def isInstanceOf(*classes):
    def test(obj): return isinstance(obj, classes)
    return test

def hasAttributes(*attributes):
    def test(obj):
        for each in attributes:
            if not hasattr(obj, each): return False
        return True
    return test

def hasMethods(*methods):
    def test(obj):
        for each in methods:
            try:
                attr = getattr(obj, each)
            except AttributeError:
                return False
            return callable(attr)
        return True
    return test

class RequiredFeature(object):
    '''
    An attribute descriptor to "declare" required features
    '''
    def __init__(self, feature, assertion=noAssertion):
        self.feature = feature
        self.assertion = assertion
    def __get__(self, obj, T):
        return self.result # <-- will request the feature upon first call

    def __getattr__(self, name):
        assert name == 'result', "Unexpected attribute request other then 'result'"
        self.result = self.request()
        return self.result

    def request(self):
        obj = features[self.feature]
        assert self.assertion(obj), \
            "The value %r of %r does not match the specified criteria" \
            % (obj, self.feature)
        return obj

class Component(object):
    '''
    Abstract/symbolic base class for components

    # Some python module defines a Bar component and states the dependencies
    # We will assume that:
    #  - Console denotes an object with a method writeLine(string)
    #  - AppTitle denotes a string that represents the current application name
    #  - CurrentUser denotes a string that represents the current user name
    >>> class Bar(Component):
    ...     con   = RequiredFeature('Console', hasMethods('writeLine'))
    ...     title = RequiredFeature('AppTitle', isInstanceOf(str))
    ...     user  = RequiredFeature('CurrentUser', isInstanceOf(str))
    ...     def __init__(self):
    ...         self.X = 0
    ...     def printYourself(self):
    ...         self.con.writeLine('-- Bar instance --')
    ...         self.con.writeLine('Title: %s' % self.title)
    ...         self.con.writeLine('User: %s' % self.user)
    ...         self.con.writeLine('X: %d' % self.X)

    # Some other python module defines a basic Console component
    >>> class SimpleConsole:
    ...     def writeLine(self, s):
    ...         print s

    # Yet another python module defines a better Console component
    >>> class BetterConsole:
    ...     def __init__(self, prefix=''):
    ...         self.prefix = prefix
    ...     def writeLine(self, s):
    ...         # do it better
    ...         print s

    # Some third python module knows how to discover the current user's name
    >>> def getCurrentUser():
    ...     return 'Some User'

    # Finally, the main python script specifies the application name,
    # decides which components/values to use for what feature,
    # and creates an instance of Bar to work with
    >>> features.provide('AppTitle', 'Inversion of Control ... The Python Way')
    >>> features.provide('CurrentUser', getCurrentUser)
    >>> features.provide('Console', SimpleConsole)

    # features.provide('Console', BetterConsole, prefix='-->') # <-- transient lifestyle
    # features.provide('Console', BetterConsole(prefix='-->')) # <-- singleton lifestyle

    >>> bar = Bar()
    >>> bar.printYourself()
    -- Bar instance --
    Title: Inversion of Control ... The Python Way
    User: Some User
    X: 0

    # Evidently, none of the used components needed to know about each other
    # => Lose coupling goal achieved
    '''
    pass

def _test():
    import doctest, components
    doctest.testmod(components)

if __name__ == '__main__':
    _test()
