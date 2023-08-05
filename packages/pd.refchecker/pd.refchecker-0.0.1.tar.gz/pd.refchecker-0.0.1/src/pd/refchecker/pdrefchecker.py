#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This propgram developed to scan xmlrpc server tree and edit attributes
of some interfaces by external applicaton.

Used:

    pdrefchecker [<SWITCHES>] <URL>

Switches:

    -v
        Be verbose;
        
    -t <int> 
        Timeout;
        
    -l
        Use lock
        
    -p  
        Lockpath                
        
Arguments:

    <URL>
        Access point to xmlrpc getReference() routine.
        

Sample::

    pdrefchecker -v -p -v \
        http://theman:12345678@localhost:8080/Root/++site++etc/Catalog/reference
       
       
The pdrefchecker scanned external links to search glitches.

$Id: pdrefchecker.py 49399 2008-01-13 07:24:23Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49399 $"

def _(s) : return s

from xmlrpclib import ServerProxy, Error
import getopt, fcntl, signal, sys, os, tempfile
from urllib import quote,unquote
import urllib

def alarm_handler(url) :
    print >>sys.stderr,"Timeout on request of %s" % url
    sys.exit(1)

def main() :
    isverbose = False
    islock = False
    #islock = True
    lock_path = '/var/run/pdrefchecker/pdrefchecker.lock'
    lib_path = '/var/lib/pdrefchecker/'
    iswait = True 
    timeout = 10
    isskip = False
        
    opts,vals = getopt.getopt(sys.argv[1:],"vmsl:p:wt:") 

    if len(vals) < 1 :
        print __doc__
        sys.exit(1)

    rpcserver = vals[0]

    for opt,val in opts :
        if opt in ["-v"] :
            isverbose = True
        elif opt in ["-m"] :
            islock = False
        elif opt in ["-l"] :
            lock_path = val
        elif opt in ["-p"] :
            lib_path = val
        elif opt in ["-w"] :
            iswait = False
        elif opt in ["-t"] :
            timeout = arg
        elif opt in ["-s"] :
            isskip = True
        else :
            print >>sys.stderr, "Unknown key %s" % opt

        if islock :
            try: 
                _lock_file=open(lock_path, 'r+')
            except: 
                _lock_file=open(lock_path, 'w+')

            try: 
                fcntl.flock(_lock_file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except Exception,msg:
                print >>sys.stderr,"Повторный запуск процесса",msg
                sys.exit(2)
                
            _lock_file.write(str(os.getpid()))
            _lock_file.flush()
    
    if isverbose :
        print "Reference getting"
        
    urls = ServerProxy(rpcserver).getReference()

    if isskip :
        if isverbose :
            print "List external reference"
        for url in urls :
            print url
    else :
        if isverbose :
            print "Reference scan has now begun"
        
        for url in urls :
            
            signal.signal(signal.SIGALRM,lambda sig,frame,url=url:alarm_handler(url))
            
            # fn = urlparse.urlparse(url)[2].split("/")[-1] or "index.html"

            signal.alarm(timeout)
            try :
                try :
                    res = urllib.urlopen(url).read()
                except Exception,msg :
                    #print >>sys.stderr,"Resource %s download error: %s" % (url,msg)
                    print "%-50s ... ERROR" % url
                    if isverbose :
                        print msg
                else :
                    print "%-50s ... OK" % url
            finally :
                signal.alarm(0)
        
        if isverbose :
            print "Successful complete"

    return 0

if __name__ == '__main__' :
    import sys
    sys.exit(main())            
