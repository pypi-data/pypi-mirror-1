#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This propgram developed to notify xmlrpc server about 
new changes in subversion.

Used:

     pdsubverionnotify.py [<SWITCHES>] <URL> <EXCHANGE FILE>
     
Switches:

    -v
        Be verbose;
        
    -l<path> 
        Path to file used to exchange urls;

    -t<int>
        Resource timeout

$Id: pdsubversionnotify.py 12966 2007-11-11 14:49:10Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12966 $"

def _(s) : return s

from xmlrpclib import ServerProxy, Error
import getopt, fcntl, signal, sys

def main() :
    isverbose = False
    islock = True
    filename = "allfiles.txt"
    lib_path = '/var/spool/pdsubverionnotify/'
    lock_path = ''
    iswait = True 
    timeout = 10

    opts,vals = getopt.getopt(sys.argv[1:],"vml:p:wt:") 

    if len(vals) != 2 :
        print __doc__
        return 0
        
    rpcserver,filename = vals

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
        else :
            print >>sys.stderr, "Unknown key %s" % opt

    lock_path = filename #os.path.join(lib_path,filename)
        
    try: 
        _lock_file=open(lock_path, 'r+')
    except Exception,msg: 
        print "Empty exchange file",msg
        return 0

    try: 
        fcntl.flock(_lock_file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except Exception,msg:
        print >>sys.stderr,"Process start dulicated",msg
        return 2
        
    #_lock_file.write(str(os.getpid()))
    #_lock_file.flush()

    def alarm_handler(url) :
        print >>sys.stderr,"Url timeout happened %s" % url
        sys.exit(1)

    if isverbose :
        print "Begin file scan"

    server = ServerProxy(rpcserver)        
    
    for url in _lock_file.xreadlines() :
        signal.signal(signal.SIGALRM,lambda sig,frame,url=url:alarm_handler(url))
        signal.alarm(timeout)
        try :
            if isverbose :
                print "Notify %s on %s" % (url,rpcserver)
            try :
                res = server.update([url])
            except Exception,msg :
                print >>sys.stderr,"Error %s on %s running" % (msg,url)
                sys.exit(4)            
            else :
                if isverbose :
                    print "Server result is",res
        finally :
            signal.alarm(0)
        
    if isverbose :
        print "Successful complete"

    _lock_file.seek(0)
    _lock_file.truncate()
    
    return 0

if __name__ == '__main__' :
    import sys
    sys.exit(main())            
