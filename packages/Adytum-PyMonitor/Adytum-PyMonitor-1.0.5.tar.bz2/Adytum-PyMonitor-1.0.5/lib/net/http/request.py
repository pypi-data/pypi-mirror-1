STATUS = 0

class Error(Exception):
    pass

class DataError(Error):
    pass

class HeaderParser(object):
    '''
    This class parses the header information in an HTTP
    request.

    For a full definition of the fields, see the following:
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html

    >>> response = r"""HTTP/1.1 401 Authorization Required\r\nDate: Thu, 10 Mar 2005 00:02:06 GMT\r\nServer: Apache/2.0.50 (Linux/SUSE)\r\nWWW-Authenticate: Basic realm="AdytumManagement"\r\nVary: accept-language,accept-charset\r\nAccept-Ranges: bytes\r\nConnection: close\r\nContent-Type: text/html; charset=iso-8859-1\r\nContent-Language: en\r\nExpires: Thu, 10 Mar 2005 00:02:06 GMT\r\n\r\n"""
    >>> p = HeaderParser(response)
    >>> p.getHTTPVersion()
    >>> p.getReturnStatusInteger()
    >>> p.getReturnStatus()
    >>> p.data
    '''
    def __init__(self, data):
        '''
        '''
        if data is None or data == 'None':
            raise DataError, "parser is receiving an empty request; there is nothing to parse."
        #raise "Here is the data received: %s" % str(data)
        data = data.split('\r\n')
        self.status = data[STATUS].split()
        self.data = dict([ (x.split()[0][:-1], ' '.join(x.split()[1:])) for x in data[1:] if x ])
        
    def getHTTPVersion(self):
        return self.status[0]

    def getReturnStatusInteger(self):
        return int(self.status[1])

    def getReturnStatus(self):
        return ' '.join(self.status[2:])

def _test():
    import doctest
    import request
    doctest.testmod(request)

if __name__ == "__main__":
    _test()
