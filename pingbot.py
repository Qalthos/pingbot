#    PingBot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PingBot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PingBot.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

from twisted.words.protocols.irc import IRCClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor

class PingBot(IRCClient):
    bot_name = "PingBot"
    channel = "#rit-foss-test"
    versionNum = 1
    #~ sourceURL = "http://gitorious.com/~jlew"
    lineRate = 1
    nicks = []
    aliases = {}

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        print "Joined %s" % channel

    def left(self, channel):
        """This will get called when the bot leaves the channel."""
        print "Left %s" % channel

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        if channel == self.nickname:
            if msg == 'start':
                self.nicks.append(user)
                self.msg(user, 'I eagerly await your pings.')
            else:
                self.msg(user, "I'm sorry, but the only command I understand is 'start'.")

        p = msg.split(':', 1)
        if len(p) == 2 and (p[0] in self.nicks or p[0] in self.aliases.keys()):
            nick = p[0]
            ping = p[1]
            time = datetime.now()
            print("At {0}, {1} said {2} to {3}".format(time, user, ping, nick))

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]

        if old_nick in self.nicks:
            self.aliases[new_nick] = old_nick
        elif old_nick in self.aliases.keys() and new_nick not in self.nicks:
            self.aliases[new_nick] = self.aliases[old_nick]
            del self.aliases[old_nick]


class PingBotFactory(ReconnectingClientFactory):
    active_bot = None

    def __init__(self, protocol=PingBot):
        self.protocol = protocol
        self.channel = protocol.channel
        IRCClient.nickname = protocol.bot_name
        IRCClient.realname = protocol.bot_name


if __name__ == '__main__':
    # create factory protocol and application
    f = PingBotFactory()

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
