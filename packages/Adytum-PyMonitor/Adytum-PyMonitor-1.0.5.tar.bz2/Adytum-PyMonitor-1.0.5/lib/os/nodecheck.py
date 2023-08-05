'''
I have written and rewritten small little scripts to monitor file
or directory check sums/md5 sums, that I got tired of it. I never
want to write those again, if I can help it.

A company I do work for had a need for this kind of thing, so in
anticipation of being asked to set something up, I wrote this code.

Additional inspiration was a python recipe on ASPN:

http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/156178

It was for windows machines only, so I thought of how I could do 
the same thing on UNIX. I googled for the win32 fucntions/methods
I saw in the recipe, and with a grudging sense of duty (credit 
where credit's due), I have to mention that I spent some time
digging through the following section of the MSDN:

http://msdn.microsoft.com/library/default.asp?url=/library/en-us/fileio/base/directory_management_reference.asp

However, I used almost none of that when writing my code. Most M$ 
interfaces cause me to feel ill, and their "Directory Management" 
is no exception.

'''
import os
import stat
import md5
import time
import copy

# constants
NOTIFY_CHANGE_CONTENTS = 1
NOTIFY_CHANGE_SIZE = 2
NOTIFY_CHANGE_ATIME = 3
NOTIFY_CHANGE_CTIME = 4
NOTIFY_CHANGE_MTIME = 5
NOTIFY_CHANGE_OWNERSHIP = 6
NOTIFY_CHANGE_PERMISSIONS = 7
NOTIFY_CHANGE_ALL = 8

DIR = 'directory'
CHR = 'character'
BLK = 'block'
REG = 'regular file'
FIFO = 'named pipe'
LNK = 'symbolic link'
SOCK = 'socket'

MODE = 0
INONUM = 1
DEV = 2
NLINK = 3
UID = 4
GID = 5
SIZE = 6
ATIME = 7
MTIME = 8
CTIME = 9

class NodeNotFound(Exception):
    pass

class DirectoryNotFound(NodeNotFound):
    pass

class FileNotFound(NodeNotFound):
    pass

class CheckNode(object):

    def __init__(self, path=''):
        self.path = path
        self.setNodeData()

    def setNodeData(self):
        self.stats = os.stat(self.path)
        self.nodetype = self.getType(self.stats)
        self.bytes = self.stats[SIZE]
        self.atime = self.stats[ATIME]
        self.ctime = self.stats[CTIME]
        self.mtime = self.stats[MTIME]
        self.owner = '%s:%s' % (self.stats[UID], self.stats[GID])
        self.mode = stat.S_IMODE(self.stats[MODE])
        self.md5sum = self.getMD5Sum()

    def getType(self, stats):
        mode = stats[MODE]
        if stat.S_ISDIR(mode): return DIR
        elif stat.S_ISCHR(mode): return CHR
        elif stat.S_ISBLK(mode): return BLK
        elif stat.S_ISREG(mode): return REG
        elif stat.S_ISFIFO(mode): return FIFO
        elif stat.S_ISLNK(mode): return LNK
        elif stat.S_ISSOCK(mode): return SOCK

    def getMD5Sum(self):
        m = md5.new(self.sumString())
        return m.hexdigest()

    def sumString(self):
        return '%s%s%s%s%s%s%s' % (self.nodetype, str(self.bytes), 
            str(self.mtime), self.owner, str(self.mode),
            str(self.atime), str(self.ctime))

class CheckDir(CheckNode):
        
    def setNodeData(self, path=''):
        '''
        setNodeData() must be overritten because not only does the base 
        class' method not have the data we want, we need to be able to call
        a method that re-checks the status of the node and recalculate the 
        md5 sum.

        super setNodeData() has to be called after contents is set due to the
        fact that the sumString() method that this class overrides is called 
        (indirectly) from super setNodeData(), and this sumString() refers to
        self.contents.
        '''
        if not path:
            path = self.path
        contents = os.listdir(path)
        contents.sort()
        self.contents = contents
        super(CheckDir, self).setNodeData()

    def sumString(self):
        base = super(CheckDir, self).sumString()
        contents = ''.join(self.contents)
        return '%s%s' % (base, contents)

class CheckFile(CheckNode):

    def setNodeData(self, path=''):
        '''
        setNodeData() must be overritten because not only does the base 
        class' method not have the data we want, we need to be able to call
        a method that re-checks the status of the node and recalculate the 
        md5 sum.

        super setNodeData() has to be called after contents is set due to the
        fact that the sumString() method that this class overrides is called 
        (indirectly) from super setNodeData(), and this sumString() refers to
        self.contents.

        In this case, we have no reason to keep track of file contents after
        md5 sum calculation, so we dump it immediately.
        '''
        if not path:
            path = self.path
        contents = open(path).read()
        self.contents = contents
        super(CheckFile, self).setNodeData()
        self.contents = ''
    
    def sumString(self):
        base = super(CheckFile, self).sumString()
        return '%s%s' % (base, self.contents)

class NodeData(object):

    pass

class NotificationServer(object):
    
    def __init__(self, checks=[], flags=[], callback=None, timeout=2):
        '''
        checks      - a list of CheckNode (or child class) instances
        flags       - a list of flags used to filter changes
        callback    - function to execute on changes for which filters have been set
        timeout     - length of time between checks, in seconds
        '''
        self.checks = checks
        self.flags = flags
        self.callback = callback
        self.timeout = timeout

    def runOnce(self):
        '''
        * loop through every check that has been added
        * check for changes that match the passed flag
        * for each change, execute the callback
        '''
        for check in self.checks:
            old_data = copy.copy(check.__dict__)
            check.setNodeData()
            new_data = check.__dict__
            if new_data['md5sum'] != old_data['md5sum']:
                self.callback(old_data, new_data)

    def runDelay(self):
        '''
        * loop through every check that has been added
        * check for changes that match the passed flag
        * for each change, execute the callback
        '''
        self.runOnce()
        time.sleep(self.timeout)
        

    run = runDelay

