import itertools

class Sequence(object):
    '''
    Actually, this is really what's called the 'Look and Say Sequence'
    sequence. Conway's Sequence has a starting digit of '3'. The
    integer sequence beginning with a single digit in which the
    next term is obtained by describing the previous term. Starting
    with 1, the sequence would be defined by "1, one 1, two 1s, one
    2 one 1," etc., and the result is 1, 11, 21, 1211, 111221, ....
    Similarly, starting the sequence instead with the digit d for
    gives d, 1d, 111d, 311d, 13211d, 111312211d, 31131122211d,
    1321132132211d, ...,

    >>> seq = Sequence()
    >>> seq.next()
    '1'
    >>> seq.next()
    '11'
    >>> seq.next()
    '21'
    >>> seq.next()
    '1211'
    >>> seq.next()
    '111221'
    >>> seq.next()
    '312211'
    >>> seq.getNElements(10) 
    ['1', '11', '21', '1211', '111221', '312211', '13112221', '1113213211', '31131211131221', '13211311123113112211']
    >>> seq.slice(2,4) 
    ['21', '1211']

    >>> seq = Sequence(start='1')
    >>> seq.getNthElement(2)
    '11'
    >>> seq.getNthElement(4)
    '1211'
    >>> seq.getNthElement(10)
    '13211311123113112211'
    >>> len(seq.getNthElement(31))
    5808

    >>> seq = Sequence(start='3')
    >>> seq.getNthElement(2)
    '13'
    >>> seq.getNthElement(4)
    '3113'
    >>> seq.getNthElement(10)
    '31131122211311123113322113'
    >>> seq.getNElements(10) 
    ['3', '13', '1113', '3113', '132113', '1113122113', '311311222113', '13211321322113', '1113122113121113222113', '31131122211311123113322113']
    '''
    def __init__(self, start='1'):
        self.start = start
        self.num = start
        self._results = self._generator()

    def _get_current(self, position=0):
        count = 1
        current_part = self.num[position]
        try:
            while(self.num[position + count] == current_part):
                count += 1
        except IndexError:
            # we've reached the end of the number
            pass
        conway_part = str(count) + str(current_part)
        next_part_start = position + count
        return (next_part_start, conway_part)

    def _next(self):
        return_val = self.num
        accum = ''
        next = 0
        while(next < len(self.num)):
            next, this_part = self._get_current(position=next)
            accum = accum + this_part
        self.num = accum
        return return_val

    def _generator(self):
        while(self.num):
            yield self._next()

    def getNElements(self, n_last, n_first=0):
        '''
        For getting element slices, we really want a
        new instance each time. Otherwise we'll be
        getting results we don't expect.
        '''
        s = Sequence(self.start)
        return list(itertools.islice(s._results, n_first, n_last))

    def getNthElement(self, n):
        return self.getNElements(n, n-1)[0]

    def next(self):
        try:
            return self._results.next()
        except StopIteration:
            pass

    def slice(self, start, stop):
        return self.getNElements(stop, start)

def _test():
    import doctest, conway
    doctest.testmod(conway)

if __name__ == '__main__':
    _test()
