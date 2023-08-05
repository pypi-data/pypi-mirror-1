#!/usr/bin/env python

"""
Monitors a custom Subversion commit message directory for new
messages and then posts the commit comments of the new messages
to the channel.
"""
__revision__ = "$Id: Subversion.py"

import plugins

import os
import re
import time
import getopt
import urllib2
import urlparse

import conf
import utils
import ircmsgs
import webutils
import ircutils
import privmsgs
import registry
import callbacks

import copy
import sets
from adytum.os.nodecheck import CheckDir, NotificationServer
from adytum.os.nodecheck import NOTIFY_CHANGE_CONTENTS

def configure(advanced):
    from questions import output, expect, anything, something, yn
    conf.registerPlugin('Subversion', True)
    if yn("""This plugin offers a monitor that will listen to a particular
             directory for file additions and then parse new files for
             information pertaining to subversion commits, posting the
             parsed information to the channel.
             Would you like this monitor to be enabled?""", default=False):
        conf.supybot.plugins.Subversion.monitor.setValue(True)

conf.registerPlugin('Subversion')
conf.registerChannelValue(conf.supybot.plugins.Subversion, 'monitor',
    registry.Boolean(False, """Determines whether the
    svn monitor is enabled.  This monitor will watch for new files in a
    directory, and parse them for subversion commit information."""))
conf.registerChannelValue(conf.supybot.plugins.Subversion.monitor, 'directory',
    registry.String('/tmp/svncommits', """The directory the monitor will listen to
    for file additions."""))
conf.registerChannelValue(conf.supybot.plugins.Subversion.monitor, 'interval',
    registry.PositiveInteger(30, """The number of seconds the monitor will wait
    between checks for newly added files to the monitored directory."""))

class Subversion(callbacks.PrivmsgCommandAndRegexp):
    def __init__(self):
        self.channel = list(conf.supybot.channels())[0]
        self.nextMsgs = {}
        callbacks.PrivmsgCommandAndRegexp.__init__(self)
        timeout = conf.supybot.plugins.Subversion.monitor.interval.value
        #self.log.info("Got '%s' for timeout" % timeout)
        directory = conf.supybot.plugins.Subversion.monitor.directory.value
        #self.log.info("Got '%s' for directory" % directory)
        #self.log.info('callbacks.world.ircs[0]: %s' % str(dir(callbacks.world.ircs[0])))
        #self.log.info('conf.supybot.channels: %s' % str(dir(conf.supybot.channels)))
        #self.log.info('conf.supybot.channels: %s' % str(conf.supybot.channels.__dict__))
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        flags = [NOTIFY_CHANGE_CONTENTS]
        check = CheckDir(directory)
        checks = [check]
        self.ns = NotificationServer(checks, flags, self.nsCallback, timeout=timeout)
        #while True:
        #    self.ns.run()
        #self.nsCallback('oldstuff', 'newstuff')

    def nsCallback(self, olddata, newdata):
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
        #msg = 'Test message from Subversion plugin: {olddata:%s}, {newdata:%s}' % (olddata, newdata)
        if dir_action:
            msg = 'The following files were %s: %s' % (dir_action, str(files))
            self.log.info(msg)
            msg = ircmsgs.notice(self.channel, msg)
            callbacks.world.ircs[0].queueMsg(msg)
        #while True:
        #    self.ns.run()
        #self.nsCall

    def die(self):
        callbacks.PrivmsgCommandAndRegexp.die(self)

Class = Subversion

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
