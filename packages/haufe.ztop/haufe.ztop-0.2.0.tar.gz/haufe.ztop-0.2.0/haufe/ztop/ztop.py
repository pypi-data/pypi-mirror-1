#! /usr/bin/env python
'''ztop [-i interval] [-s shortPeriod] [-m medPeriod] [-l longPeriod] [-n numberLongRequests [-t time] [-r]] [[-b] requestsBasename] [[-d] startDate]

displays request information by analysis of the Zope requests log file
identified by *requestsBasename* and *startDate*.

Information contains summaries for up to three periods: 'short', 'med'
and 'long'. Their length is given by *shortPeriod* (default: 120),
*medPeriod* (default: 600) and *longPeriod* (default: 3600) in seconds.
Summaries contain load averaged over the period, number of finished
requests, request rate, average, min, max and median request times (in ms)
and the *numberLongRequests* (default: 3) longest requests in this period.
A period length of "0" suppresses information about this period.

The information is repeated every *interval* seconds.
*interval* defaults to the value of *shortPeriod* or 120.
A "0" value causes 'ztop' to stop after one display.

The '-t' option tells 'ztop' to display information for *time*
and then to stop. *time* is an ISO datetime or time value,
e.g. '2004-08-03T12:00:00' or '12:00:00'.

The '-r' option tells 'ztop' to display information for the last
restart time and then to stop. '-r' is equivalent to '-t <restartTime>'.
This is meant to facilitate the analysis of restarts.

*requestsBasename* is either an instance tag (in which case it expands
to '/var/log/zope/*requestsBasename*/zope_requests.') or
the name of a zope requests file (not ending in '.') or of
a zope requests file family (ending in '.').
*requestsBasename* defaults to the instance tag 'Main'.
*startDate* must have the format year, month and day, each with 2 digits
e.g. '040803'. It defaults to the current date. Note that *requestsBasename*
must be an instance tag or a family name, when you default *startDate*.
'''
INSTANCE_BASE = '/var/log/zope'

import sys, getopt
from time import time, localtime, mktime, strftime, sleep
from re import compile
from os.path import isdir

from Sampler import Sampler
from Feeder import Feeder


def usage(text=None):
    if text: print >> sys.stderr, text
    print >> sys.stderr, __doc__
    sys.exit(text is not None)
    
def main(argv=sys.argv):
    interval = None
    shortPeriod = 120; medPeriod = 600; longPeriod = 3600
    numberLongRequests = 3
    showTime = showForRestart = None
    requestsBasename = 'Main'
    startDate = None
    
    try: opts, args = getopt.getopt(argv[1:],
                                    'i:s:m:l:n:t:b:d:rh'
                                    )
    except getopt.error, e: usage(str(e))
    
    for opt, arg in opts:
        if opt == '-i': interval = int(arg)
        elif opt == '-s': shortPeriod = int(arg)
        elif opt == '-m': medPeriod = int(arg)
        elif opt == '-l': longPeriod = int(arg)
        elif opt == '-n': numberLongRequests = int(arg)
        elif opt == '-t': showTime = arg
        elif opt == '-r': showForRestart = True
        elif opt == '-h': usage()
        elif opt == '-b': requestsBasename = arg
        elif opt == '-d': startDate = arg
        else: raise NotImplementedError('option: ' + opt)
        
    if len(args) >= 1: requestsBasename = args[0] 
    if len(args) >= 2: startDate = args[1] 
    
    s = Sampler(shortPeriod, medPeriod, longPeriod)
    f = _getFeeder(s, requestsBasename, startDate)
    f.feed()
    
    # abuse s
    s.numberLongRequests = numberLongRequests
    
    if showForRestart:
        showTime = s.getRestartTime()
        if showTime is None: sys.exit()
    if showTime:
        if isinstance(showTime, str): showTime = _toEpoch(showTime)
        _show(s, showTime); sys.exit()
        
    if interval is None:
        interval = shortPeriod
        if not interval: interval = 120
    if not interval: _show(s); sys.exit()
    
    while True:
        _show(s)
        sleep(interval)
        f.feed()
        
def _formatTime(ti, tiFormat='%Y-%m-%dT%H:%M:%S'):
    return strftime(tiFormat, localtime(ti))
    
def _formatFloat(fl):
    return _formatNumber(fl, 1000)
    
def _formatNumber(no, scale=1):
    return _formatField(no is not None and '%d' % int(no * scale) or '-')
    
def _formatReq(req, format=_formatFloat):
    r = req[1]
    i = r.find('VirtualHostRoot')
    if i >= 0: r = r[i + 16:]
    return '%s %s' % (format(req[0]), r)
    
def _formatFields(fields):
    return ''.join([_formatField(f) for f in fields])
    
def _formatField(f):
    return f.rjust(8)
    
def _show(sampler, showTime=None,):
    numberLongRequests = sampler.numberLongRequests
    if showTime is None: showTime = time()
    print 80*'='
    print _formatTime(showTime)
    info = sampler.getInfo(showTime)
    rst = info.get('restartTime')
    if rst: print 'Restart:\t', _formatTime(rst)
    pending = info.get('pending')
    if pending:
        print 'Pending:'
        for p in pending: print _formatField('') + _formatReq(p, _formatTime)
    fields = 'load\treqs\trate\tavg\tmin\tmax\tmedian'.split('\t')
    for i in 'short med long'.split():
        id = info.get(i)
        if id:
            print 80*'-'
            print _formatFields([i] + fields)
            lrs = id['requests']
            l = min(len(lrs), numberLongRequests)
            print ''.join([
              _formatField(''),
              _formatField('%.2f' % id['load']), 
              _formatNumber(id['no']),
              _formatField('%.2f' % id['rate']),
              _formatFloat(id['average']),
              _formatFloat(id['min']),
              _formatFloat(id['max']),
              _formatFloat(id['median']),
              ])
            for j in range(l):
                print _formatField('') + _formatReq(lrs[j])
                
def _toEpoch(ti, digs_=compile('\d+').findall):
    'convert time or datetime string into sec since epoch.'''
    nums = map(int, digs_(ti))
    if len(nums) > 6: raise ValueError('wrong datetime format: ' + ti)
    if len(nums) == 6 and nums[0] < 1000: nums[0] += 2000
    if len(nums) < 6: nums = localtime()[:6-len(nums)] + tuple(nums)
    nums = tuple(nums) + (0,0,-1)
    return mktime(nums)
    
    
def _getFeeder(sampler, requestsBasename, startDate):
  # expand instance tag
    if '/' not in requestsBasename \
       and isdir('%s/%s' % (INSTANCE_BASE, requestsBasename)):
        requestsBasename = '%s/%s/zope_requests.' % (INSTANCE_BASE, requestsBasename)
    if startDate and not requestsBasename.endswith('.'):
        requestsBasename += '.'
        
    return Feeder(sampler, requestsBasename, startDate or None)
    
    
if __name__ == '__main__': 
    main()
