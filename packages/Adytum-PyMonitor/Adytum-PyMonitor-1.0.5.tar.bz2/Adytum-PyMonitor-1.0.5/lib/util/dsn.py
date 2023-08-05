def createDsn(**kw):
    '''
    # check named parameters
    >>> createDsn()
    Traceback (most recent call last):
    AssertionError: You must specify 'dbtype'.
    >>> createDsn(dbname='ziff', user='me', password='secret')
    Traceback (most recent call last):
    AssertionError: You must specify 'dbtype'.
    >>> createDsn(dbtype='mysql', user='me', passwd='secret', dbname='ziff')
    Traceback (most recent call last):
    AssertionError: You must use the parameter name 'password'.
    >>> createDsn(dbtype='mysql', user='me', pwd='secret', dbname='ziff')
    Traceback (most recent call last):
    AssertionError: You must use the parameter name 'password'.

    # try different forms
    >>> createDsn(dbtype='mysql', dbname='ziff')
    'mysql:///ziff'
    >>> createDsn(dbtype='mysql', dbname='ziff', user='')
    'mysql:///ziff'
    >>> createDsn(dbtype='mysql', user='me', dbname='ziff')
    'mysql://me/ziff'
    >>> createDsn(dbtype='mysql', user='me', password='secret', dbname='ziff')
    'mysql://me:secret/ziff'
    >>> createDsn(dbtype='mysql', user='me', password='secret', host='', dbname='ziff')
    'mysql://me:secret/ziff'
    >>> createDsn(dbtype='mysql', user='me', password='secret', host='copwaf01', dbname='ziff')
    'mysql://me:secret@copwaf01/ziff'
    >>> createDsn(dbtype='mysql', user='', password='', host='copwaf01', dbname='ziff')
    'mysql://copwaf01/ziff'
    >>> createDsn(dbtype='mysql', user='me', password='secret', host='copwaf01', port='', dbname='ziff')
    'mysql://me:secret@copwaf01/ziff'
    >>> createDsn(dbtype='mysql', user='me', password='secret', host='copwaf01', port='6669', dbname='ziff')
    'mysql://me:secret@copwaf01:6669/ziff'
    >>> createDsn(dbtype='custom', dbname='mydb', path='/var/db', filename='mydb.dbz')
    'custom:///mydb?path=/var/db;filename=mydb.dbz;'
    '''
    assert(kw is not None), \
        "You must pass named parameters in the function call."
    assert(kw.has_key('dbtype')), \
        "You must specify 'dbtype'."
    assert(True not in [ x in ['passwd', 'pwd'] 
        for x in kw.keys() ]), \
        "You must use the parameter name 'password'."

    standard_params = ['dbtype', 'dbname', 'user', 'password', 'host', 'port']
    used_params = {}
    for param in standard_params:
        if kw.has_key(param):
            val = kw.pop(param)
            if bool(val):
                used_params[param] = val
    non_standard_params = kw

    dsn = '%s://' % used_params['dbtype']
    if used_params.has_key('user'):
        dsn += '%s' % used_params['user']
        if used_params.has_key('password'):
            dsn += ':%s' % used_params['password']
    if used_params.has_key('host'):
        host = used_params['host']
        if used_params.has_key('user'):
            host = '@' + host
        dsn += '%s' % host
        if used_params.has_key('port'):
            dsn += ':%s' % used_params['port']
    if used_params.has_key('dbname'):
        dsn += '/%s' % used_params['dbname']
    if non_standard_params:
        dsn += '?'
    for option, value in non_standard_params.items():
        dsn += '%s=%s;' % (option, value)
    return dsn

def parseDsn(dsn):
    import re

def _test():
    import doctest, dsn
    doctest.testmod(dsn)

if __name__ == '__main__':
    _test()

