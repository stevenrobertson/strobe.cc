# Copyright (c) 2009 Steven Robertson.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or
# later, as published by the Free Software Foundation.

NAME="Google_Code_RSS_IRC_Bridge_Bot"
VERSION="0.1"

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task

import feedparser

import re
import sys
import urllib2

class AnnounceBot(irc.IRCClient):

    username = "%s-%s" % (NAME, VERSION)
    sourceURL = "http://strobe.cc/"

    # I am a terrible person.
    instance = None

    # Intentionally 'None' until we join a channel
    channel = None

    # Prevent flooding
    lineRate = 3

    def signedOn(self):
        self.join(self.factory.channel)
        AnnounceBot.instance = self

    def joined(self, channel):
        self.channel = self.factory.channel

    def left(self, channel):
        self.channel = None

    def trysay(self, msg):
        """Attempts to send the given message to the channel."""
        if self.channel:
            try:
                self.say(self.channel, msg)
                return True
            except: pass

class AnnounceBotFactory(protocol.ReconnectingClientFactory):
    protocol = AnnounceBot
    def __init__(self, channel):
        self.channel = channel

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

class FeedReader:
    _schema = 'http://code.google.com/feeds/p/%s/updates/basic'

    def __init__(self, project):
        self.project = project
        self.entries = {}

    def update(self):
        """Returns list of new items."""
        feed = feedparser.parse(self._schema % self.project)
        added = []
        for entry in feed['entries']:
            if entry['id'] not in self.entries:
                self.entries[entry['id']] = entry
                added.append(entry)
        return added

def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)

def announce(feed):
    new = feed.update()
    for entry in new:
        msg = '%s: %s' % (strip_tags(entry['title']), entry['link'])
        if AnnounceBot.instance:
            AnnounceBot.instance.trysay(msg.replace('\n', '').encode('utf-8'))

if __name__ == '__main__':
    # All per-project customizations should be done here

    AnnounceBot.nickname = 'quodlibot'
    fact = AnnounceBotFactory("#quodlibet")
    feed = FeedReader('quodlibet')
    reactor.connectTCP('irc.oftc.net', 6667, fact)

    # Don't reannounce every update on startup
    feed.update()

    update_task = task.LoopingCall(announce, feed)
    update_task.start(600, now=False)

    reactor.callLater(10, announce, feed)

    reactor.run()

