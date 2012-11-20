#!/usr/bin/python

from optparse import OptionParser
import getpass
import sys, dl
import time
from timeobject import TimeObject

sys.setdlopenflags(dl.RTLD_NOW | dl.RTLD_GLOBAL)

import purple

# The information below is needed by libpurple
__NAME__ = "RyanSpam"
__VERSION__ = "1.0"
__WEBSITE__ = "N/A"
__DEV_WEBSITE__ = "www.aqnichol.com"

class Spammer(object):

    def __init__(self, core, username, password, spamUser, interval, destTime):
        self.core = core
        self.username = username
        self.password = password
        self.spamUser = spamUser
        self.interval = interval
        self.destTime = destTime
        # information for the spam loop
        self.lastIteration = None
        self.is_connected = False
        self.buddy_online = False
        self.core.signal_connect('signed-on', self.signed_on)
        self.core.signal_connect('buddy-signed-on', self.buddy_signed_on)
        self.core.signal_connect('buddy-signed-off', self.buddy_signed_off)

    def connect(self):
        # connect to the account
        protocol = purple.Protocol('prpl-aim')
        self.account = purple.Account(self.username, protocol, self.core)
        self.account.new()
        # authenticate
        self.account.set_password(self.password)
        self.account.set_enabled(True) # will initiate the signon process

    def signed_on(self, user, proto):
        self.is_connected = True
        self.lastIteration = None
        self.buddy = purple.Buddy(self.spamUser, self.account)
        self.account.add_buddy(self.spamUser, group='Buddies')

    def buddy_signed_off(self, user, proto):
        print 'buddy signed off: ' + user
        if user == self.spamUser: self.buddy_online = False

    def buddy_signed_on(self, user, proto):
        print 'buddy signed on: ' + user
        if user == self.spamUser: self.buddy_online = True

    def iteration(self):
        if not self.is_connected or not self.buddy_online: return
        interval = self.interval.second_offset()
        currentTime = time.time()
        if self.lastIteration == None:
            self.send_time(currentTime)
        elif currentTime - self.lastIteration >= float(interval):
            self.send_time(currentTime)

    def send_time(self, now):
        if self.buddy.online: print 'spam buddy is online'
        else: print 'spam buddy is not online'
        self.lastIteration = now
        print 'sending spam to ' + self.spamUser
        cTime = TimeObject.current_time()
        if cTime.is_after(self.destTime):
            print 'passed time: %s > %s' % (str(cTime), str(self.destTime))
        else:
            timeRemaining = cTime.time_until(self.destTime)
            msg = str(timeRemaining) + ' left, bro'
            conv = purple.Conversation('IM', self.account, self.spamUser)
            conv.new()
            conv.im_send(msg)
            print 'sent: ' + msg + ' to aim:' + self.spamUser

if __name__ == '__main__':
    # Sets initial parameters
    core = purple.Purple(__NAME__, __VERSION__, __WEBSITE__, __DEV_WEBSITE__,
            debug_enabled=False, default_path="/tmp")

    # Initializes libpurple
    core.purple_init()

    parser = OptionParser()
    parser.add_option('-u', '--user', dest='user', help='the AIM username')
    parser.add_option('-v', '--victim', dest='victim', help='the AIM victim user')
    parser.add_option('-p', '--pass', dest='password',
        help='the optional AIM password')
    parser.add_option('-i', '--interval', dest='interval',
        help='the interval at which the program will send spam')
    parser.add_option('-d', '--dest', dest='destination',
        help='the destination time of day')

    (options, arg) = parser.parse_args()
    username, password, interval, victim, destination = [None]*5
    if not options.user:
        sys.stdout.write('Enter AIM account: ')
        username = sys.stdin.readline().rstrip()
    else: username = options.user
    if not options.password:
        password = getpass.getpass()
    else: password = options.password
    if not options.interval:
        interval = TimeObject(hour=0, minute=30, second=0)
    else: interval = TimeObject(options.interval)
    if not options.victim:
        sys.stdout.write('Enter AIM victim: ')
        victim = sys.stdin.readline().rstrip()
    else: victim = options.victim
    if not options.destination:
        destination = TimeObject(hour=17, minute=30, second=0)
    else: destination = TimeObject(options.destination)

    print 'Using aim:%s to spam aim:%s at interval of %s until %s' % (username, victim, str(interval), str(destination))

    spammer = Spammer(core, username, password, victim, interval, destination)
    spammer.connect()

    while True:
        try:
            core.iterate_main_loop()
            spammer.iteration()
            time.sleep(0.01)
        except KeyboardInterrupt:
            break

