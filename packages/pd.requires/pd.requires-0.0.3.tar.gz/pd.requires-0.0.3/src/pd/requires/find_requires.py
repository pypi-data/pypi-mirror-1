#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This script can find requires in python sources
Used:
    find_requires [<MODULE> [...]] [-f (RPM|PYPI)] [-r]
    
    -f - Dependencies will be printed in RPM or PYPI format,
         it is PYPI by default;
        
    -r - The name of file will be printed
         after dependence emited by them.

    The program must be run in directory contains module.


$Id: find_requires.py 12907 2007-11-10 17:26:55Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12900 $"

def _(s) : return s

import pd.find
from requires import file_requires
from provides import file_provides
import re, sys, getopt, os

match = re.compile("python[0-9]\.[0-9]\((?P<name>[^)]+)\)").match

def check(path,res) :
    req = {}
    for x,y in file_requires((x.path for x in pd.find.find(path,lambda x : x.isreg() and x.check_regex(".*.py$")))) :
        req.setdefault(x,[]).append(y)            

    d = {}
    for x,y in file_provides(
            [x.path for x in pd.find.find(path,lambda x : x.isreg() and x.check_regex(".*.py$"))]
            ) :
        x = match(x).groupdict()['name']
        l = []
        lx = x.split(".")
        for i in range(0,len(lx)) :
            d.setdefault(tuple(lx[0:i]),set()).add(tuple(lx[i:]))

    sreq = set()    
    for x,ys in req.items() :
        x = tuple(match(x).groupdict()['name'].split("."))
        
        for y in ys :
            y = y[len(path):]
            y=tuple(path.split("/")[-1:]+y.split("/")[1:-1])
                
            if y in d :
                if x not in d[y] :
                    sreq.add("python2.4(%s)" % ".".join(x))
            else :                
                sreq.add("python2.4(%s)" % ".".join(x))

    sprov = set(( x for x,y in
        file_provides(
            [x.path for x in pd.find.find(path,lambda x : x.isreg() and x.check_regex(".*.py$"))]
        )
    ))     

    for item in sreq-sprov :
        res.setdefault(item,set()).update(req[item])

    return res

def main() :
    format = "PYPI"
    use_print_filename = False

    opts,modules = getopt.getopt(sys.argv[1:],"f:r") 

    if not modules :
        print __doc__
        sys.exit(1)        

    for opt,val in opts :
        if opt in ["-f"] :
            if val in ["PYPI","RPM"] :
                format = val
            else :
                print >>sys.stderr,"Format must be PYPI or RPM"
                sys.exit(1)
        elif opt in ["-r"] :
            use_print_filename = True
        else :
            print >>sys.stderr, "Unknown switch %s" % opt

    d = {}
    for item in modules :
        check(os.path.abspath(item),d)
        
    for item in sorted(d) :
        if format == "PYPI" :
            print match(item).groupdict()['name'],
        else :
            print item,
        if use_print_filename :
            print ":"
            for file in sorted(d[item]) :
                print "\t",file
        print ""

if __name__ == '__main__' :
    main()    
    
