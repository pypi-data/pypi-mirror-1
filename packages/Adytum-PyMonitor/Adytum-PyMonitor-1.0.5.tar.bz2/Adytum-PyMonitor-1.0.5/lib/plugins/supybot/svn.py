#!/usr/bin/env python

"""
Monitors a custom Subversion commit message directory for new
messages and then posts the commit comments of the new messages
to the channel.

Here are the additions I made to /usr/local/bin/supybot:

    from adytum.plugins.supybot import svn

    channel = list(conf.supybot.channels())[0]
    ns_nextrun = time.time() + conf.supybot.svn.monitor.interval()
    svnsb = svn.SupybotNS(conf.supybot.svn, world.ircs[0], log, channel, schedule)
    log.info('Created SupybotNS instance %s' % str(svnsb))
    schedule.addEvent(svnsb.ns.runOnce, ns_nextrun, 'nsrun')
    log.info('Scheduled directory watcher...')

I added the following to supybot/src/conf.py:

    supybot.register('svn', registry.Boolean(True, ''))
    supybot.svn.register('monitor', registry.Boolean(True, ''))
    supybot.svn.monitor.register('directory', registry.String('/tmp/svncommits',
    '''Where to look for monitoring svn changes.'''))
    supybot.svn.monitor.register('interval', registry.PositiveInteger(30,
    '''How often to look at monitor directory.'''))
"""
import sets
import time
from adytum.os.nodecheck import CheckDir, NotificationServer
from adytum.os.nodecheck import NOTIFY_CHANGE_CONTENTS
from adytum.plugins.svn import convert
from supybot.src import ircmsgs

class SupybotNS(object):

    def __init__(self, svnconf, irc, log, channel, schedule):
        self.conf = svnconf
        check = CheckDir(self.conf.monitor.directory())
        self.channel = channel
        checks = [ check ]
        flags = [ NOTIFY_CHANGE_CONTENTS ]
        self.ns = NotificationServer(checks, flags, self.supybotCallback)
        self.irc = irc
        self.log = log
        self.schedule = schedule

    def supybotCallback(self, olddata, newdata):
        self.log.info('Supybot notification server callback called...')
        old = sets.Set(olddata['contents'])
        new = sets.Set(newdata['contents'])
        dir_action = ''
        # check which files have been deleted
        if len(old) > len(new):
            files = list(old.difference(new))
            dir_action = 'removed'
        # check which files have been added
        if len(old) < len(new):
            files = list(new.difference(old))
            dir_action = 'added'
        if dir_action == 'added':
            directory = self.conf.monitor.directory()
            for aFile in files:
                try:
                    #msg = 'The following files were %s: %s' % (dir_action, str(files))
                    c = convert.Commit2IRCMessage('/%s/%s' % (directory, aFile))
                    msg = c.render()
                    msg = msg.replace('\n', ' ')
                    msg = msg.replace('\r', ' ')
                except:
                    msg = 'Could not parse file %s' % aFile
                self.log.info(msg)
                msg = ircmsgs.notice(self.channel, msg)
                self.irc.queueMsg(msg)
        ns_nextrun = time.time() + self.conf.monitor.interval()
        self.schedule.addEvent(self.ns.runOnce, ns_nextrun)

