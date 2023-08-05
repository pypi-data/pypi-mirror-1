Short package description
=========================

Package developed to provide possibility send notification
to xmlrpc-servers when data in svn has been updated.

Package provide utility:

    pdsubversionnotify.py
        The program started, read update list from file and
        send it to server. When file and acquired it truncated.
        
        Used:
        
            pdsubversionnotify.py  <URL XMLRPC> <EXCHANGE FILE> 
            

Sample
------

In subversion post-commit-hook please, write ::

    #!/bin/sh
    REPOS="$1"
    REV="$2"
    
    export LC_ALL=ru_RU.UTF-8
    svnlook changed --revision $REV $REPOS|
        grep -v "^D" |
        cut -b 5-|
        awk '{print "https://code.dreambot.ru/svn/"$0}' >>/var/tmp/allfiles.txt
        
    pdsubversionnotify <URL XMLRPC> /var/tmp/allfiles.txt
    
            
    
            