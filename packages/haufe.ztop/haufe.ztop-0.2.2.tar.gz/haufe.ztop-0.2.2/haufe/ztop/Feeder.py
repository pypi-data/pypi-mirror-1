#       $Id: Feeder.py,v 1.1 2004-08-03 13:52:21 dieter Exp $
'''Feeder.

Reads a sequence a 'zope_requests' files and adds the request lines
to a sampler.

Handles Zopes log rotation.
'''

from os.path import exists
from DateTime import DateTime
from Sampler import _toEpoch

class Feeder:

    def __init__(self, sampler,
                 base='/var/log/zope/Main/zope_requests.',
                 startDate=None,
                 ):
        '''sets up feeder to feed from a Zope requests file or file family
        given by *base* and starting at *startDate*.
        
        *startDate* defaults to today.
        '''
        self._sampler = sampler
        self._base = base
        self._isFamily = isFamily = base.endswith('.')
        if isFamily:
          # will break in 2100
            startDate = (
              startDate
              and DateTime(2000+int(startDate[:2]),
                           int(startDate[2:4]),
                           int(startDate[4:6])
                           )
              or DateTime().earliestTime()
              )
            # we add to avoid problems when daylight saving changes
            self._date = startDate + 0.5
            
    def feed(self):
        '''feed as much request info to sampler as possible.'''
        fed = False; sampler = self._sampler
        while True:
            line = self._readline()
            if not line: return fed
            sampler.addLine(line); fed = True
            
    _file = _pos = None
    def _readline(self):
        while True:
          # get file
            fo = self._file
            if fo is None:
                fn = self._base
                if self._isFamily: fn += self._date.strftime('%y%m%d')
                if exists(fn): fo = self._file = open(fn)
                if self._pos is not None: del self._pos
                # read line
            if fo is not None:
                if self._pos: fo.seek(self._pos); del self._pos
                line = fo.readline()
                if line: return line
                self._pos = fo.tell()
                # switch file
            if not self._nextFile(): return
            
    def _nextFile(self):
        if not self._isFamily: return
        limit = DateTime().latestTime(); base = self._base
        d = self._date + 1
        while d <= limit:
            if exists(base + d.strftime('%y%m%d')): self._date = d; return True
            d += 1
            
            
            
            
            
