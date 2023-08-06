#! /usr/bin/env python
'''zanalyse [-i intervall] [-n numberLongRequests] [[-b] requestsBasename] [[-d] startDate]

prints an 'sar' like requests summary from the Zope requests log file
identified by *requestsBasename* and *startDate*.

The '-i' option specifies the granularity in minutes. It defaults to "10".

*requestsBasename* is either an instance tag (in which case it expands
to '/var/log/zope/*requestsBasename*/zope_requests.') or
the name of a zope requests file (not ending in '.') or of
a zope requests file family (ending in '.').
*requestsBasename* defaults to the instance tag 'Main'.
*startDate* must have the format year, month and day, each with 2 digits
e.g. '040803'. It defaults to the current date. Note that *requestsBasename*
must be an instance tag or a family name, when you default *startDate*.
'''

import getopt, sys

from Sampler import Sampler
from ztop import _getFeeder, _show


def usage(text=None):
    if text: print >> sys.stderr, text
    print >> sys.stderr, __doc__
    sys.exit(text is not None)
    
    
def main(argvi=sys.argv):
    interval = 10
    noLong = 10
    requestsBasename = 'Main'
    startDate = None
    
    try: opts, args = getopt.getopt(argv[1:], 'i:n:b:d:h')
    except getopt.error, e: usage(str(e))
    
    for opt, arg in opts:
        if opt == '-i': interval = int(arg)
        elif opt == '-n': noLong = int(arg)
        elif opt == '-b': requestsBasename = arg
        elif opt == '-d': startDate = arg
        elif opt == '-h': usage()
        else: raise NotImplementedError('option: ' + opt)
        
    if len(args) >= 1: requestsBasename = args[0] 
    if len(args) >= 2: startDate = args[1] 
    
    interval *= 60
    
    s = Sampler(interval, 0, 0)
    s.numberLongRequests = noLong
    f = _getFeeder(s, requestsBasename, startDate)
    f.feed()
    
    bounds = s.getTimeBounds()
    if bounds is None: return
    
    ct = bounds[0]; et = bounds[1]
    while ct < et: _show(s, ct); ct += interval
    
if __name__ == '__main__': 
    main()
