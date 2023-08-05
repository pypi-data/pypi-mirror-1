class ListConfig(list):
    '''
    # list check
    >>> l = [1, 2, 3, 'a', 'b', 'c']
    >>> cfg = ListConfig(l)
    >>> cfg
    [1, 2, 3, 'a', 'b', 'c']

    # list-with-dict check
    >>> d = {'test': 'value'}
    >>> l = [1, 2, 3, d]
    >>> cfg = ListConfig(l)
    >>> cfg[3].test
    'value'
    '''
    def __init__(self, aList):
        self.processList(aList)

    def __call__(self, **kw):
        # XXX just supporting one keyword call now
        key = kw.keys()[0]
        # XXX just supporting dicts now
        for i in self:
            if isinstance(i, dict) and i.has_key(key) and i.get(key) == kw.get(key):
                return i

    def processList(self, aList):
        for element in aList:
            if isinstance(element, dict):
                self.append(DictConfig(element))
            elif isinstance(element, list):
                self.append(ListConfig(element))
            else:
                self.append(element)

class IterConfig(ListConfig):
    '''
    The reason  for implementing IterConfig is not to provide the
    memory-savings associated with iterators and generators, but rather
    to benefit from the convenience of the next() method.

    # list-with-dict check
    >>> d = {'test': 'value'}
    >>> l = [1, 2, 3, d]
    >>> cfg = IterConfig(l)
    >>> cfg.next()
    1
    >>> cfg.next()
    2
    >>> cfg.next()
    3
    >>> cfg.next().test
    'value'
    '''
    def __init__(self, aList):
        super(IterConfig, self).processList(aList)

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.pop(0)
        except IndexError:
            raise StopIteration
                
class DictConfig(dict):
    '''
    # dict check
    >>> d = {'test': 'value'}
    >>> cfg = DictConfig(d)
    >>> cfg.test
    'value'

    # dict-with-list check
    >>> l = [1, 2, 3, 'a', 'b', 'c']
    >>> d = {'test': 'value', 'mylist': l}
    >>> cfg = DictConfig(d)
    >>> cfg.test
    'value'
    >>> cfg.mylist
    [1, 2, 3, 'a', 'b', 'c']

    # one more level of recursion
    >>> l = [1, 2, 3, d]
    >>> d = {'test': 'value', 'list': l}
    >>> cfg = DictConfig(d)
    >>> cfg.list[3].test
    'value'

    # and even deeper
    >>> d = {'higher': {'lower': {'level': [1, 2, 3, [4, 5, 6, {'key': 'val'}]]}}}
    >>> cfg = DictConfig(d)
    >>> cfg.higher.lower.level[3][3].key
    'val'

    # simple demonstration
    >>> test_dict = { 'some': 'val', 'more': ['val1', 'val2', 'val3'], 'jeepers': [ {'creep': 'goosebumps', 'ers': 'b-movies'}, ['deeper', ['and deeper', 'and even deeper']]]}
    >>> cfg = DictConfig(test_dict)
    >>> cfg.some
    'val'
    >>> for i in cfg.more:
    ...  i
    'val1'
    'val2'
    'val3'
    >>> cfg.jeepers[0].creep
    'goosebumps'
    >>> cfg.jeepers[0].ers
    'b-movies'
    >>> cfg.jeepers[1][0]
    'deeper'
    >>> cfg.jeepers[1][1][1]
    'and even deeper'

    # and now let's explore some recursion
    >>> test_dict2 = {'val1': 'a', 'val2': 'b', 'val3': '4c'}
    >>> test_list = [1, 2, 3, 'a', 'b', 'c', test_dict2]
    >>> test_dict3 = {'level1': test_dict2, 'level2': [test_dict2, test_dict2, test_list]}
    >>> test_dict4 = {'higher1': {'lower1': test_dict2, 'lower2': test_list, 'lower3': test_dict3}}
    >>> cfg = DictConfig(test_dict4)
    >>> cfg.higher1.lower1.val1
    'a'
    >>> cfg.higher1.lower2[0]
    1
    >>> cfg.higher1.lower2[4]
    'b'
    >>> cfg.higher1.lower2[6].val1
    'a'
    >>> cfg.higher1.lower3.level1.val2
    'b'
    >>> cfg.higher1.lower3.level2[1].val3
    '4c'
    >>> cfg.higher1.lower3.level2[2][6].val1
    'a'

    # a potential real-world example:
    >>> email1 = ['joe@blo.com', 'bob@spy1.mil', 'alice@spy2.mil']
    >>> email2 = ['jgurl@co.us', 'zippy@slo.com']
    >>> groups1 = [{'level': 1, 'emails': email1}, {'level': 2, 'emails': email2}]
    >>> groups2 = [{'level': 2, 'emails': email1}, {'level': 1, 'emails': email2}]
    >>> escalation1 = {'enabled': True, 'groups': groups1}
    >>> escalation2 = {'enabled': True, 'groups': groups2}
    >>> escalation3 = {'enabled': False}
    >>> host1 = {'name': 'host001.myco.com', 'escalation': escalation1}
    >>> host2 = {'name': 'host002.myco.com', 'escalation': escalation2}
    >>> host3 = {'name': 'host003.myco.com', 'escalation': escalation3}
    >>> host4 = {'name': 'host004.myco.com', 'escalation': escalation2}
    >>> host5 = {'name': 'host005.myco.com', 'escalation': escalation2}
    >>> host6 = {'name': 'host006.myco.com', 'escalation': escalation3}
    >>> hosts1 = [host1, host2, host3, host4, host5, host6]
    >>> hosts2 = [host2, host5]
    >>> hosts3 = [host3, host4, host6]
    >>> defaults1 = {'count': 40, 'ok': 10, 'error': 20, 'warn': 15}
    >>> defaults2 = {'count': '150'}
    >>> service1 = {'type': 'ping', 'name': 'Host Reachable', 'hosts': hosts1, 'defaults': defaults1}
    >>> service2 = {'type': 'smtp', 'name': 'Mail Service', 'hosts': hosts2, 'defaults': defaults2}
    >>> service3 = {'type': 'http', 'name': 'Web Service', 'hosts': hosts3, 'defaults': defaults2}
    >>> services = {'services': [service1, service2, service3]}
    >>> cfg = DictConfig(services)
    >>> cfg.services[0].type
    'ping'
    >>> cfg.services[1].name
    'Mail Service'
    >>> cfg.services[2].defaults.count
    '150'
    >>> cfg.services[0].hosts[5].name
    'host006.myco.com'
    >>> cfg.services[0].hosts[5].escalation.enabled
    False
    >>> cfg.services[0].hosts[4].name
    'host005.myco.com'
    >>> cfg.services[0].hosts[4].escalation.enabled
    True
    >>> cfg.services[0].hosts[4].escalation.groups[0].level
    2
    >>> cfg.services[0].hosts[4].escalation.groups[0].emails[2]
    'alice@spy2.mil'
    >>> cfg.doesntexist
    None
    >>> cfg.services[0].hosts[4].doesntexists
    None
    >>> cfg.this.doesnt.exist
    None
    >>> if cfg.this.doesnt.exist: 
    ...   print "no!"
    '''
    def __init__(self, aDict):
        self.processDict(aDict)

    def __getattr__(self, attr):
        try: 
            return self.__dict__[attr]
        except: 
            #return ''
            return DictConfig({})

    def __repr__(self):
        rep = self.__dict__
        if not rep:
            return str(None)
        return str(self.__dict__)

    def processDict(self, aDict):
        for key, val in aDict.items():
            if isinstance(val, dict):
                subobj = DictConfig(val)
                setattr(self, key, subobj)
            elif isinstance(val, list):
                l = ListConfig(val)
                setattr(self, key, l)
            else:
                setattr(self, key, val)
        self.update(aDict)

def _test():
    import doctest, base
    return doctest.testmod(base)

if __name__ == '__main__':
    _test()

