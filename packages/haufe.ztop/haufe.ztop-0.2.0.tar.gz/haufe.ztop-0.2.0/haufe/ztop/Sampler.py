#       $Id: Sampler.py,v 1.8 2005-01-06 07:08:02 dieter Exp $
'''Sampler.

Samples individual request lines and stores them in
a data structure to support efficient statistics.
'''

from __future__ import division
from time import time as pyTime, mktime
from BTrees.IOBTree import IOBTree


class Sampler:
    def __init__(self, short=120, med=600, long=3600, retain=2):
        '''create a Sampler with default periods *short*, *med*, *long*
        (seconds) which keeps information for at most *retain* (days).'''
        self._short = int(short)
        self._med = int(med)
        self._long = int(long)
        self._retain = int(retain * 86400) # now in seconds
        # internal data
        self._events = IOBTree()
        self._restarts = []
        self._pending = {}
        
    def addLine(self, request):
        '''update internal state according to *request*.'''
        request = request.rstrip()
        ti, status, time, type, id, req = request.split(None, 5)
        ti = _toEpoch(ti)
        if type == '0':
          # restart
            self._addEvent(ti, type='r')
            self._restarts.append(ti)
            self._pending = {}
        elif type == '+':
          # new request
            self._pending[id] = (ti, req)
            # we discard (silently) closing events we did not get the start
        elif id in self._pending:
          # finished request
            del self._pending[id]
            self._addEvent(ti, req, float(time))
            
    def getInfo(self, time=None, short=None, med=None, long=None):
        '''returns statistical information for up to three periods
          ending at *time*.
        
          "time" defaults to the current time.
        
          The duration of the three periods are controlled
          by *short* (default "120"), "med" (default "600")
          and *long* (default "3600") given in seconds.
          A period with a non-positive value suppresses the corresponding
          statistics.
        
          The information is returned in a dictionary with keys:
        
           'time' -- analysis time
        
           'pending' -- sequence of tuples (startime, request) for
                        requests not finished at *time*.
        
           'restartTime' -- the time (sec since epoch) of the last restart or 'None'
        
           'short', 'med', 'long' -- information for the respective period
                    or missing, when the period was disabled
        
          The information for a period is a dictionary with keys:
        
           'duration' -- in s
        
           'load' -- Zopes load during this period, i.e. the time
             spend executing any request divided by the available time.
        
             Note that 'load' is never larger than the number of threads
             Zope is running with.
        
           'no' -- number of requests finished in period
        
           'min' -- minimal time for requests finished in period
        
           'max' -- maximal time ....
        
           'average' -- average time ...
        
           'median' -- median time ...
        
           'rate' -- number of finished requests per second
        
           'requests' -- a sequence of tuples (time, request), sorted decreasing
             by time; this sequence includes both finished and unfinished requests.
             This sequence can be used to determine long running requests 
        '''
        if time is None: time = pyTime()
        time = int(time)
        info = {}
        info['time'] = time
        info['pending'] = pending = self.getPending(time)
        info['restartTime'] = self.getRestartTime(time)
        locs = locals()
        for period in 'short med long'.split():
            p = locs.get(period)
            if p is None: p = getattr(self, '_'+period)
            if p: info[period] = self.getInfoForPeriod(time, p, pending)
        return info
        
    def getInfoForPeriod(self, time, duration, pending=None):
        '''determine info for period ending at *time* with *duration*.
        
        If *pending* is given, it must be the pending requests at *time*.
        If not given, it is determined.
        '''
        time = int(time); start = time-duration; lsum = 0.0
        if pending is None: pending = self.getPending(time)
        finished = []; unfinished = []
        for r in pending:
            unfinished.append((time-r[0], r[1]))
            lsum += time - max(r[0], start)
        for et, el in self._events.items(start, time-1):
            for e in el:
                ty, pending = e[:2]
                if ty == 'r':
                    for r in pending:
                        unfinished.append((et-r[0], r[1]))
                        lsum += et - max(r[0], start)
                if ty == 'f':
                    ri = e[2:]
                    finished.append(ri)
                    lsum += min(ri[0], et-start)
        info = {}
        finished.sort(); n = len(finished)
        info['duration'] = duration
        info['no'] = n
        info['rate'] = n / duration
        if n:
            info['min'] = finished[0][0]
            info['max'] = finished[-1][0]
            info['median'] = finished[n // 2][0]
            info['average'] = sum([r[0] for r in finished]) / n
        else: info['min'] = info['max'] = info['median'] = info['average'] = None
        finished += unfinished
        finished.sort(); finished.reverse()
        info['requests'] = finished
        info['load'] = lsum / duration
        return info
        
    def getPending(self, time=None):
        '''the requests pending at *time*.'''
        if time is None: time = pyTime()
        time = int(time)
        events = self._events; above = events.keys(time)
        if above:
            pending = events[above[0]][0][1]
        else: pending = self._pending.values()
        return pending
        
    def getRestartTime(self, time=None):
        '''the latest restart time (s since epoch) at or before time.'''
        if time is None: time = pyTime()
        time = int(time)
        restartTime = None
        for ti in self._restarts:
            if ti > time: break
            restartTime = ti
        return restartTime
        
    def getTimeBounds(self):
        '''return earliest and latest event times (sec since epoch) or
        'None' (in case there are not events).'''
        events = self._events
        if not events: return
        ets = events.keys()
        return ets[0], ets[-1]
        
    def _addEvent(self, time, req=None, duration=None, type='f'):
        '''add an event.'''
        events = self._events
        # remove oldies
        for t in list(events.keys(None, time-self._retain)): del events[t]
        # form new event
        e = (type, tuple(self._pending.values()))
        if type == 'f': e += (duration, req)
        # add
        el = events.get(time)
        if el is None: el = events[time] = []
        el.append(e)
        
        
def _toEpoch(ts):
    '''convert time string *ts* in sec since epoch.'''
    year, month, day, hour, min, sec = map(int, (
      ts[:2], ts[2:4], ts[4:6],
      ts[7:9], ts[9:11], ts[11:13],
      )
                                           )
    # this fails from 2100 on.
    year += 2000
    return int(mktime((year, month, day, hour, min, sec) + (0,0,-1)))
