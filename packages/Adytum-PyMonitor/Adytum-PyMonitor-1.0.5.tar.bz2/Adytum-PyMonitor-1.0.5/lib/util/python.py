'''
Python extensions.
'''
class Switch(object):
    '''
    Title: Readable switch construction without lambdas or dictionaries
    Submitter: Brian Beck
    Last Updated: 2005/04/26
    Version no: 1.7
    Category: Extending
    Description: Python's lack of a 'switch' statement has garnered
    much discussion and even a PEP. The most popular substitute uses
    dictionaries to map cases to functions, which requires lots of defs
    or lambdas. While the approach shown here may be O(n) for cases,
    it aims to duplicate C's original 'switch' functionality and structure
    with reasonable accuracy.
    Source: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/410692

    This class provides the functionality we want. You only need to look at
    this if you want to know how this works. It only needs to be defined
    once, no need to muck around with its internals.

    # The following example is pretty much the exact use-case of a dictionary,
    # but is included for its simplicity. Note that you can include statements
    # in each suite.
    >>> v = 'ten'
    >>> for case in switch(v):
    ...     if case('one'):
    ...         print 1
    ...         break
    ...     if case('two'):
    ...         print 2
    ...         break
    ...     if case('ten'):
    ...         print 10
    ...         break
    ...     if case('eleven'):
    ...         print 11
    ...         break
    ...     if case(): # default, could also just omit condition or 'if True'
    ...         print "something else!"
    ...         # No need to break here, it'll stop anyway
    10

    # break is used here to look as much like the real thing as possible, but
    # elif is generally just as good and more concise.

    # Empty suites are considered syntax errors, so intentional fall-throughs
    # should contain 'pass'
    >>> c = 'z'
    >>> for case in switch(c):
    ...     if case('a'): pass # only necessary if the rest of the suite is empty
    ...     if case('b'): pass
    ...     # ...
    ...     if case('y'): pass
    ...     if case('z'):
    ...         print "c is lowercase!"
    ...         break
    ...     if case('A'): pass
    ...     # ...
    ...     if case('Z'):
    ...         print "c is uppercase!"
    ...         break
    ...     if case(): # default
    ...         print "I dunno what c was!"
    c is lowercase!

    # As suggested by Pierre Quentel, you can even expand upon the
    # functionality of the classic 'case' statement by matching multiple
    # cases in a single shot. This greatly benefits operations such as the
    # uppercase/lowercase example above:
    >>> import string
    >>> c = 'A'
    >>> for case in switch(c):
    ...     if case(*string.lowercase): # note the * for unpacking as arguments
    ...         print "c is lowercase!"
    ...         break
    ...     if case(*string.uppercase):
    ...         print "c is uppercase!"
    ...         break
    ...     if case('!', '?', '.'): # normal argument passing style also applies
    ...         print "c is a sentence terminator!"
    ...         break
    ...     if case(): # default
    ...         print "I dunno what c was!"
    c is uppercase!

    # Since Pierre's suggestion is backward-compatible with the original recipe,
    # I have made the necessary modification to allow for the above usage.
    '''
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

switch = Switch

import operator
from UserDict import UserDict

class Multicast(UserDict):
    '''
    Class multiplexes messages to registered objects

    Title: Multicasting on objects
    Submitter: Eduard Hiti (other recipes)
    Last Updated: 2001/12/23
    Version no: 1.1
    Category: OOP
    Description: Use the 'Multicast' class to multiplex messages/attribute
    requests to objects which share the same interface.
    Source: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52289

    >>> import StringIO

    >>> file1 = StringIO.StringIO()
    >>> file2 = StringIO.StringIO()
    
    >>> multicast = Multicast()
    >>> multicast[id(file1)] = file1
    >>> multicast[id(file2)] = file2

    >>> assert not multicast.closed

    >>> multicast.write("Testing")
    >>> assert file1.getvalue() == file2.getvalue() == "Testing"
    
    >>> multicast.close()
    >>> assert multicast.closed
    '''
    def __init__(self, objs=[]):
        UserDict.__init__(self)
        for alias, obj in objs: self.data[alias] = obj

    def __call__(self, *args, **kwargs):
        "Invoke method attributes and return results through another Multicast"
        return self.__class__( [ (alias, obj(*args, **kwargs) ) for alias, obj in self.data.items() ] )

    def __nonzero__(self):
        "A Multicast is logically true if all delegate attributes are logically true"
        return operator.truth(reduce(lambda a, b: a and b, self.data.values(), 1))

    def __getattr__(self, name):
        "Wrap requested attributes for further processing"
        return self.__class__( [ (alias, getattr(obj, name) ) for alias, obj in self.data.items() ] )

    def __setattr__(self, name, value):
        if name == "data":
            self.__dict__[name]=value
            return
        for object in self.values():
            setattr(object, name, value)

def _test():
    import doctest, python
    doctest.testmod(python)

if __name__ == '__main__':
    _test()
