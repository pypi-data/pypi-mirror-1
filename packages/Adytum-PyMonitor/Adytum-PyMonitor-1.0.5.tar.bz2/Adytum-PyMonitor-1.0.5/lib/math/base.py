NOTATION10 = '0123456789'
NOTATION36 = '0123456789abcdefghijklmnopqrstuvwxyz'
NOTATION65 = '-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
NOTATION68 = '$,-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~'
NOTATION69 = '%+-.0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~'
NOTATION70 = "!'()*-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~"
NOTATION90 = "!'#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_abcdefghijklmnopqrstuvwxyz{|}"

legal_bases = [10, 36, 65, 68, 69, 70, 90]

class BaseConvert(object):
    '''
    "Base" class for base conversions ;-)
    '''
    __metaclass__ = type
    base            = None
    notation        = None
    notation_map    = None

    def _convert(self, n):
        '''
        Private function for doing conversions; returns a list
        '''
        if True not in [ isinstance(1, x) for x in [long, int, float] ]:
            raise TypeError, 'parameters bust be numbers'
        converted = []
        quotient, remainder = divmod(n, self.base)
        converted.append(remainder)
        if quotient != 0:
            converted.extend(self._convert(quotient))
        return converted
    """
    def convert(self, n):
        '''
        General conversion function
        '''
        nums = self._convert(n)
        nums.reverse()
        return self.getNotation(nums)
    """
    def convert(self, n, tobase=None, frombase=10):
        try:
            n = int(n)
        except:
            raise "The first parameter of 'convert' needs to be an integer!"
        if not tobase:
            tobase = self.base
        '''
        nums = [ self.notation_map[x] for x in str(n) ]
        nums.reverse()

        total = 0
        for number in nums:
            total += 1 * number
            number *= frombase
        if total == 0:
            return '0'
        
        converted = []
        while total:
            total, remainder = divmod(total, tobase)
            converted.append(self.notation[remainder])
        ''' 
        converted = [ self.notation[x] for x in self._convert(n) ]
        converted.reverse()    
        return ''.join(converted)

    def getNotation(self, list_of_remainders):
        '''
        Get the notational representation of the converted number
        '''
        return ''.join([ self.notation[x] for x in list_of_remainders ])

doc_template = '''
    >>> b       = Base%s()
    >>> zero    = b.convert(0)
    >>> ten     = b.convert(10)
    >>> hund    = b.convert(100)
    >>> thou    = b.convert(1000)
    >>> mil     = b.convert(1000000)
    >>> bil     = b.convert(100000000)
    >>> goog    = b.convert(10**10)
    >>> print (zero, ten, hund, thou, mil, bil, goog)
    >>> zero    = b.convert(zero, newbase=10, oldbase=b.base)
    >>> ten     = b.convert(ten, newbase=10, oldbase=b.base)
    >>> hund    = b.convert(hund, newbase=10, oldbase=b.base)
    >>> thou    = b.convert(thou, newbase=10, oldbase=b.base)
    >>> mil     = b.convert(mil, newbase=10, oldbase=b.base)
    >>> bil     = b.convert(bil, newbase=10, oldbase=b.base)
    >>> goog    = b.convert(goog, newbase=10, oldbase=b.base)
    >>> print (zero, ten, hund, thou, mil, bil, goog)
'''

# build classes for whatever notations exist
import new
for base in [ str(x) for x in legal_bases ]:
    base_klass = globals()['BaseConvert']
    klass_name = 'Base'+base
    notation = eval('NOTATION'+base)
    notation_map = dict([ (y, x) for x, y in enumerate(notation) ])
    #klass = type(klass_name, (base_klass,), {})
    #    {'__metaclass__':type(base_klass())})
    klass = new.classobj(klass_name, (base_klass,), {'__doc__':doc_template%base})
    klass.base = int(base)
    klass.notation = notation
    klass.notation_map = notation_map
    globals()[klass_name] = klass


def _test():
    import doctest, base
    doctest.testmod(base)

if __name__ == '__main__':
    _test()
