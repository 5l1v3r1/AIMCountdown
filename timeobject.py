#!/usr/bin/python

from datetime import datetime

class TimeObject(object):
    """ An object for representing time in hh:mm:ss format """
    def __init__(self, origStr=None, hour=None, minute=None, second=None):
        if origStr:
            comps = map(lambda x: int(x), origStr.split(':'))
            self.minute, self.hour = 0,0
            if len(comps) == 1: self.second = comps[0]
            elif len(comps) == 2:
                self.minute = comps[0]
                self.second = comps[1]
            else:
                self.hour = comps[0]
                self.minute = comps[1]
                self.second = comps[2]
        else:
            self.hour, self.minute, self.second = hour, minute, second

    def second_offset(self):
        return self.second + (self.minute * 60) + (self.hour * 60 * 60)

    def is_after(self, aTime):
        if aTime.hour < self.hour: return True
        elif self.hour < aTime.hour: return False
        if aTime.minute < self.minute: return True
        elif self.minute < aTime.minute: return False
        if aTime.second < self.second: return True
        elif self.second < aTime.second: return False
        return False

    def time_until(self, aTime):
        if not self.is_after(aTime):
            return aTime.time_until(self)
        diff = self.second_offset() - aTime.second_offset()
        second = diff % 60
        minute = (diff / 60) % 60
        hour = diff / 60 / 60
        return TimeObject(second=second, minute=minute, hour=hour)

    def __str__(self):
        return '%d:%02d:%02d' % (self.hour, self.minute, self.second)

    @staticmethod
    def current_time():
        dt = datetime.now()
        return TimeObject(hour=dt.hour, minute=dt.minute, second=dt.second)

