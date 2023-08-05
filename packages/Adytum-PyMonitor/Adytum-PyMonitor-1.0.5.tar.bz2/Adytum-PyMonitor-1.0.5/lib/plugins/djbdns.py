import re
import itertools

class DNSFile(file):
    def __init__(self, filename):
        super(DNSFile, self).__init__(filename)
        self.marker = '0'
        self.lines = self.readlines()

    def getit(self, line):
        if re.match('^%s' % self.marker, line):
            return line

    def getRecords(self, initial_string):
        pass
    def getNameSerials(self):
        pass
    def getNameServers(self):
        pass
    def getMXRecords(self):
        self.marker = '@'
        for i in itertools.ifilter(self.getit, self.lines):
            yield MXRecord(i)
    def getHosts(self):
        pass
    def getAliases(self):
        pass
    

class Record(object):
    def __init__(self, record):
        self.rec = record
        self.sep = ':'
        self.name = ''
        self.ip = ''
        self.ttl = 0
        self.NAME = 0
        self.IP = 1
        self.TTL = 2
    def getName(self):
        if self.name:
            return self.name
        return self.rec.split(self.sep)[self.NAME]
    def getIP(self):
        if self.ip:
            return self.ip
        return self.rec.split(self.sep)[self.IP]
    def getTTL(self):
        if self.ttl:
            return self.ttl
        return self.rec.split(self.sep)[self.TTL]

class MXRecord(Record):
    def __init__(self, record):
        self.rec = record
        self.sep = ':'
        self.name = ''
        self.ip = ''
        self.ttl = 0
        self.host = ''
        self.dist = 0
        self.NAME = 0
        self.IP = 1
        self.HOST = 2
        self.DIST = 3
        self.TTL = 4
        super(Record, self).__init__()
    def getHost(self):
        if self.host:
            return self.host
        return self.rec.split(self.sep)[self.HOST]
    def getDistance(self):
        if self.dist:
            return self.dist
        return self.rec.split(self.sep)[self.DIST]
    def getTTL(self):
        if self.ttl:
            return self.ttl
        return self.rec.split(self.sep)[self.TTL]
