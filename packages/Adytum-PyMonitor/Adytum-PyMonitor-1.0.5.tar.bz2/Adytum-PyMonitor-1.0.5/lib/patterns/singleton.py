class Singleton(object):
    '''
    Source: http://www.suttoncourtenay.org.uk/duncan/accu/pythonpatterns.html#singleton-and-the-borg

    >>> class C(Singleton):
    ...     pass
    >>> class D(Singleton):
    ...     pass
    >>> c = C()
    >>> d = D()
    >>> assert(id(c) != id(d)), "Oops. They're the same..."
    >>> e = D()
    >>> f = D()
    >>> assert(id(d) == id(e) == id(f)), "Oops. They're different..."
    >>> g = C()
    >>> assert(id(c) == id(g)), "Oops. They're different..."
    '''
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                Singleton, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

def _test():
    import doctest, patterns
    doctest.testmod(patterns)

if __name__ == '__main__':
    _test()

