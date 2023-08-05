#!/usr/bin/env python

"""
Monitors a custom RSSFeeds commit message directory for new
messages and then posts the commit comments of the new messages
to the channel.

Here are the additions I made to /usr/local/bin/supybot:

    from adytum.plugins.supybot import rssfeeds

    channel = list(conf.supybot.channels())[0]
    nextrun = time.time() + conf.supybot.rssfeeds.monitor.interval()
    rssfeeds_sb = rssfeeds.RSSFeeds(conf.supybot.rssfeeds, world.ircs[0], log, channel, schedule)
    log.info('Created RSSFeeds instance %s' % str(rssfeeds_sb))
    schedule.addEvent(rssfeeds_sb.getFeeds, nextrun, 'rssrun')
    log.info('Scheduled RSS feed grabber...')

I added the following to /usr/local/lib/python2.3/site-packages/supybot/src/conf.py

    supybot.register('rssfeeds', registry.Boolean(True, ''))
    supybot.rssfeeds.register('monitor', registry.Boolean(True, ''))
    supybot.rssfeeds.monitor.register('directory', registry.String('/tmp/rssfeeds',
    '''Where to store presistent data.'''))
    supybot.rssfeeds.monitor.register('interval', registry.PositiveInteger(300,
    '''How often to look at monitor directory.'''))
"""
import os
import time
import binascii
try:
    import cPickle as pickle
except:
    import pickle
from datetime import datetime

import feedparser

from supybot.src import ircmsgs

feeds = [
    'http://dirtsimple.org/rss.xml',
    'http://www.livejournal.com/users/glyf/data/rss',
    'http://www.advogato.org/person/oubiwann/rss.xml',
    'http://plone.org/rss/RSSTopic',
    'http://www.zope.org/news.rss',
    'http://www.pythonware.com/daily/rss.xml',
    'http://projects.adytum.us/tracs/PyMonitor/timeline?daysback=90&max=50&format=rss&ticket=on&wiki=on',
    'http://projects.adytum.us/tracs/adytum/timeline?daysback=90&max=50&format=rss&ticket=on&wiki=on',
]

class RSSFeeds(object):

    def __init__(self, conf, irc, log, channel, schedule):
        self.conf = conf
        self.directory = self.conf.monitor.directory()
        self.channel = channel
        self.irc = irc
        self.log = log
        self.schedule = schedule

    def getFeeds(self):
        self.log.info('Getting RSS feeds...')
        feeds_data = []
        # loop through RSS feeds
        for url in feeds:
            no_dates = False
            self.log.info('Getting RSS feed for %s...' % url)
            # get hex repr of url
            filename = binascii.hexlify(url)
            filename = os.path.join(self.directory, filename)
            # get the feed
            d = feedparser.parse(url)
            try:
                if 'pythonware' in d.feed.link:
                    # python daily has no dates, so use their entry id instead
                    no_dates = True
                    mod = d.entries[0].id.encode('ascii', 'ignore').split('#')[-1]
                else:
                    # get timestamp of the feed
                    try:
                        date = list(d.feed.modified_parsed)[:-2]
                    except:
                        # hmmm... that didn't work. 
                        date = list(d.entries[0].modified_parsed)[:-2]
                        # Must be live journal
                        #from mx import DateTime
                        #date = d.feed.lastbuilddate.encode('ascii', 'ignore')
                        #date = DateTime.DateTimeFrom(date)
                        #date = [int(x) for x in list(date.tuple())[:-2]]
                    mod = datetime(*date)
            except Exception, e:
                self.log.error('Problem during date check: %s' % e)
                no_dates = True
                mod = datetime(1900,1,1)
            # load pickled date data
            try:
                date_file = open(filename)
                last_mod = pickle.load(date_file)
                date_file.close()
            except:
                last_mod = datetime(1900,1,1)
            # if they are different, get the top entry from 
            # from the feed
            if last_mod != mod:
                try:
                    if not no_dates:
                        date = list(d.entries[0].modified_parsed)[:-2]
                        date = datetime(*date).strftime("%d %b, %I:%M%p")
                    else:
                        date = ''
                    data = {
                        'site': d.feed.title.encode('ascii', 'ignore'),
                        'title': d.entries[0].title.encode('ascii', 'ignore'),
                        'link': d.entries[0].link.encode('ascii', 'ignore'),
                        'date': date,
                    }
                    feeds_data.append(data)
                except Exception, e:
                    self.log.error('Problem during data acquisition: %s' % e)
                # save the new modified date
                date_file = open(filename, 'w+')
                pickle.dump(mod, date_file)
                date_file.close()
        self.log.info('Processed RSS feeds.')
        #msg = 'Test message from RSSFeeds plugin: {olddata:%s}, {newdata:%s}' % (olddata, newdata)
        for entry in feeds_data:
            msg = "New Blog/News Feed: %(site)s - %(title)s" % entry
            if entry['date']:
                msg += " - %(date)s" % entry
            self.log.info(msg)
            msg = ircmsgs.notice(self.channel, msg)
            self.irc.queueMsg(msg)
            msg = "%(link)s" % entry
            self.log.info(msg)
            msg = ircmsgs.notice(self.channel, msg)
            self.irc.queueMsg(msg)
        if not feeds_data:
            self.log.info('No new RSS feeds.')
        nextrun = time.time() + self.conf.monitor.interval()
        self.schedule.addEvent(self.getFeeds, nextrun)
    
