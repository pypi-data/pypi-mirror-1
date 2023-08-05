import os
import sets

if os.name == 'posix':
    TRACE_BIN = '/usr/sbin/traceroute'
else:
    TRACE_BIN = None

class Trace(object):
    '''
    >>> from traceroute import Trace
    >>> t = Trace(host='www.adytum.us')
    >>> t.call()
    >>> len(t.results.getHosts()) > 0
    '''
    def __init__(self, host='127.0.0.1', numeric=True, queries='1'):
        self.host = host
        self.numeric = numeric
        self.queries = queries
        self._setParams()
        self._setCommand()

    def _setParams(self):
        self.params = ''
        if self.numeric: 
            self.params +=' -n'
            self.mode = 'numeric'
        else:
            self.mode = 'alpha'
        if self.queries:
            self.params += ' -q %s' % self.queries

    def _setCommand(self):
        self.cmd = '%s %s %s' % (TRACE_BIN, self.params, self.host)

    def _executeCommand(self):
        p = os.popen(self.cmd)
        data = p.readlines()
        err = p.close()
        if err:
            raise RuntimeError, '%s failed w/ exit code %d' % (cmd, err)
        self.results = ParseOutput(data, self.mode)

    call = _executeCommand
    

def _parseLine(line, mode):
    if mode == 'numeric':
        try:
            (hop, sp1, host, sp2, time, units) = line.strip().split(' ')
        except:
            (hop, host, time, units) = (line[0], None, None, None)
    elif mode == 'alpha':
        try:
            (hop, sp1, host, ip, sp2, time, units) = line.strip().split(' ')
        except:
            (hop, host, time, units) = (line[0], None, None, None)
    parsed = {'hop': hop, 'host': host, 'time': time, 'timeunits': units}
    return parsed

class ParseOutput(object):

    def __init__(self, dataList, mode):
        # get rid of the first line, which is the command
        self.data = dataList[1:]
        self.mode = mode

    def getHopCount(self):
        return len(self.data)

    def getHosts(self):
        full = [ _parseLine(x, self.mode)['host'] for x in self.data ]
        return [ x for x in full if x ]

    def getLinkedHosts(self):
        '''
        This method provides a tuple of tuples of the pattern
            ((1,2), (2,3), (3,4) ... (n-1, n))
        for the purpose of using in graphs a la pydot.
        '''
        hosts = self.getHosts()
        return [ (x, hosts[hosts.index(x)+1]) for x in hosts if len(hosts) > hosts.index(x) + 1 ]

    def getLinkedDomains(self):
        '''
        This does a similar thing as the getLinkedHosts() method. In fact,
        if the .mode attribute is numeric, it just calls getLinkedHosts().
        However, if not, pull out host and subdomain from the FQDN and only
        retain domain-level name info.
        '''
        if self.mode == 'numeric':
            return self.getLinkedHosts()
        else:
            uniquer = {}
            hosts = self.getHosts()
            for host in hosts:
                domain = '.'.join(host.split('.')[-2:])
                uniquer.update({domain:hosts.index(host)})
            hosts = zip(uniquer.values(), uniquer.keys())
            hosts.sort()
            return [ (y, hosts[hosts.index((x,y))+1][1]) for x,y in hosts if len(hosts) > hosts.index((x,y)) + 1 ]
