from ConfigParser import SafeConfigParser as ConfigParser

class SVNConfigParser(object):
    '''
    The set* methods are for writing config files.

    The get* methods are for reading config files.
    '''
    def __init__(self):
        self.main_section = 'main'
        self.comments_section = 'status'
        self.parser = ConfigParser()

        self.repos_section = self.main_section
        self.repos_label = 'repository'

        self.rev_section = self.main_section
        self.rev_label = 'revision number'

        self.auth_section = self.main_section
        self.auth_label = 'user'

        self.log_section = self.comments_section
        self.log_label = 'commit log'

        self.changed_section = self.comments_section
        self.changed_label = 'changed files'

    def read(self, fromFile):
        self.parser.readfp(open(fromFile))

    def getRepository(self):
        return self.parser.get(self.repos_section, self.repos_label)

    def getRevision(self):
        return self.parser.get(self.rev_section, self.rev_label)

    def getAuthor(self):
        return self.parser.get(self.auth_section, self.auth_label)

    def getLog(self):
        return self.parser.get(self.log_section, self.log_label)

    def getChanged(self):
        return self.parser.get(self.changed_section, self.changed_label)

    def setRepository(self, repos):
        self.repos = repos

    def setRevision(self, rev):
        self.rev = rev
        
    def setAuthor(self, author):
        self.auth = author
        
    def setLog(self, log):
        self.log = log

    def setChanged(self, changed):
        self.changed = changed

    def write(self, toFile):
        self.parser.add_section(self.main_section) 
        self.parser.add_section(self.comments_section) 
        if self.repos:
            self.parser.set(self.repos_section, self.repos_label, self.repos)
        if self.rev:
            self.parser.set(self.rev_section, self.rev_label, self.rev)
        if self.auth:
            self.parser.set(self.auth_section, self.auth_label, self.auth)
        if self.log:
            self.parser.set(self.log_section, self.log_label, self.log)
        if self.changed:
            self.parser.set(self.changed_section, self.changed_label, self.changed)
        self.parser.write(open(toFile, 'w+'))

class Commit2Text(object):
    '''
    '''
    def __init__(self, parserObject):
        pass

class Commit2IRCMessage(object):
    '''
    >>> import convert
    >>> filename = '/tmp/svncommits/1111539570.67'
    >>> c = convert.Commit2IRCMessage(filename)
    >>> c.render()
    '''
    def __init__(self, fromFile):
        commit = SVNConfigParser()
        commit.read(fromFile)
        self.commit = commit

    def render(self):
        template = 'Repository: %s ** Revision: %s ** Author: %s ** Commit Comments: %s'
        return template % (self.commit.getRepository(),
            self.commit.getRevision(), self.commit.getAuthor(), 
            self.commit.getLog())
