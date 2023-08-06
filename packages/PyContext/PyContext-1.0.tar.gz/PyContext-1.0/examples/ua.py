# Simple client application for the useragent module.
from __future__ import with_statement
from useragent import HTTPUserAgent

def filter_response(f):
    line = f.read().strip()
    if not line:
        print "  user-agent not set"
    else:
        print "  user-agent is '%s'" % line

def get1():
    print "Using httplib"
    import httplib
    conn = httplib.HTTPSConnection('www.dcl.hpi.uni-potsdam.de')
    #conn.set_debuglevel(1)
    conn.request('GET', '/ua')
    r = conn.getresponse()
    filter_response(r)

def get2():
    print "Using urllib"
    import urllib2
    f = urllib2.urlopen('https://www.dcl.hpi.uni-potsdam.de/ua')
    filter_response(f)

print "Default layers"
get1()
get2()

with HTTPUserAgent("WebCOP"):
    print "Using useragent layer"
    get1()
    get2()


