#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This propgram developed to scan xmlrpc server tree and edit attributes
of some interfaces by external applicaton.

Used:

    ngxmlrpcscan [<SWITCHES>] <URL> <EXECUTABLE> [<ATTRIBUTE>  ...]

Switches:

    -v
        Be verbose;
        
    -p
        Do pause each time when exteranl routin run;
        
    -c
        Check class
        
    -s  
        Atribut are to save after external routin run;
        
    -c <CLASSNAME>
        Object checked on condition: "is object of this class".
        
    -i <INTERFACE>
        Adapt object to this interface;
    
    -n 
        Pointed object used without any scan by tree
        
    -e  
        External routin used (do print otherwize),        Filename will be
        substituted indeed substring %(file)s in this string. It supposed
        running program read filename when started and write after finish;
        
        There are other names to substitute:
        
            file
                Full path to file on disk;
                
            path
                Path to object on xmlrpcserver;
                
            name
                Name of object in xmlrpcserver.                                
                

    -q <INT>
          
        Skip first objects;   
                
        
Arguments:

    <URL>
        Scan tree will be begun on this URL. For authorization,
        you must insert login and pasword into URL. Let see
        sample bellow;
        
    <ATTRIBUTE>
        Any attribute acceptable via interface bellow.
        
Sample::

    ngxmlrpcscan.py -s -p -v \
        -c zope.app.folder.folder.Folder
        -i zope.dublincore.interfaces.IZopeDublinCore \
        -e "joe  %(file)s "
        http://theman:12345678@localhost:8080/Root/Main \
         title description        
       
       
The ngxmlrpcscan scaned object tree rooted in
http://theman:12345678@localhost:8080/Root/Main to find all folders and to
edit folder methadata via IZopeDublinCore adapter.

$Id: ngxmlrpcscan.py 51898 2008-10-21 11:36:39Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51898 $"

def _(s) : return s

from xmlrpclib import ServerProxy, Error
import getopt, fcntl, signal, sys, os, tempfile
from urllib import quote,unquote
from urlparse import urlparse,urlunparse

def walk(rpcserver,attributes,klass,interface='zope.interface.Interface') :        
    server = ServerProxy(rpcserver)
    if not klass or klass == server.klass() : 
        if server.check(interface) :
            for attr in attributes :
                yield (rpcserver,server,attr)
            
    for item in server.keys() :
        for x in walk(rpcserver + "/" + quote(str(item)),attributes,klass,interface) :
            yield x

def main() :
    isverbose = False
    ispause = False
    isedit = False
    isnotscan = False
    execute = None
    skip = 0 
        
    interface = 'zope.interface.Interface'
    klass = None
    opts,vals = getopt.getopt(sys.argv[1:],"vpsne:c:i:q:") 

    if len(vals) <= 1 :
        print __doc__
        return 0
        
    l = urlparse(vals[0])
    rpcserver = urlunparse(l[0:2] + (quote(l[2]),)+l[3:])

    attributes = vals[1:]

    for opt,val in opts :
        if opt in ["-v"] :
            isverbose = True
        elif opt in ["-p"] :
            ispause = True
        elif opt in ["-s"] :
            isedit = True
        elif opt in ["-c"] :
            klass = val
        elif opt in ["-i"] :
            interface = val
        elif opt in ["-n"] :
            isnotscan = True
        elif opt in ["-e"] :
            execute = val
        elif opt in ["-q"] :
            skip = int(val)
        else :
            print >>sys.stderr, "Unknown key %s" % opt

    if isverbose :
        print "Begin file scan"


    if isnotscan :
        lg = ( (rpcserver,ServerProxy(rpcserver),x) for x in attributes )
    else :      
        lg = walk(rpcserver,attributes,klass,interface)

    for (path,server,attr) in lg :
        if isverbose :
            print "----------" , unquote(path), ":"
            print "    ", server.klass()
            print "    ", attr
            print "-" * 80

        try :
            value = server.getattr(interface,attr) 
        except Exception,msg :
            print "Getattr",interface,attr,"fault:",msg
            continue            


        if skip :
            skip -= 1
        elif execute :
            path = unquote(path[len(rpcserver):])
            name = path.split("/")[-1]
            fn=tempfile.mktemp()+"-"+".".join(path.split("/"))

            open(fn,"w").write(value)
            if ispause :
                print "Please, enter:"
                sys.stdin.readline()
        
            os.system(execute % {"file":fn,"path":path,"name":name })
            if isedit :
                value = open(fn,"r").read()
                server.setattr(interface,attr,value)
            print ""
        else :
            print str(value)            
            
    if isverbose :
        print "Successful complete"

    return 0

if __name__ == '__main__' :
    import sys
    sys.exit(main())            
