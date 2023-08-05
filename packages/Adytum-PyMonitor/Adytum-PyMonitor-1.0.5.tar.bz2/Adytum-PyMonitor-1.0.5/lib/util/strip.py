'''
Strip utility functions
'''
import re

class NonNumeric:
    '''
    Strip non-numeric charactrs out of a string and convert it to an integer

    >>> import strip
    >>> s = strip.NonNumeric('123adfa-sdfwese00')
    >>> s.stripped
    12300

    '''
    def __init__(self, n):
        '''
        Initialize
        '''
        self.stripped = int(re.sub('[^0-9]', '', n))


