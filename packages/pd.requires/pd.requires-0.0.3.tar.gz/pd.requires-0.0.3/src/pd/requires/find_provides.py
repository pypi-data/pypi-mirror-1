#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This script can find provides in python sources.
Used:
    find_provides [<MODULE> [...]] [-f (RPM|PYPI)]
    
    -f - Dependencies will be out in RPM or PYPI format,
        it is PYPI by default;
        
    The program must be run in directory contains module.

$Id: find_provides.py 12907 2007-11-10 17:26:55Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12900 $"

def _(s) : return s

import sys
from provides import file_provides
import pd.find
import sys, os, getopt, urllib, urlparse, signal, fcntl, re

match = re.compile("^python[0-9]+\.[0-9]+\((?P<name>[^\)]+)\)$").match
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

    ls = []
    for path in (os.path.abspath(x) for x in modules):
        ls = ls+[x.path for x in pd.find.find(path,lambda x : x.isreg() and x.check_regex(".*.py$"))]

    for provide,something in file_provides(sorted(ls)) :
        if format == "PYPI" :
            provide = match(provide).groupdict()['name']
        print provide 

if __name__ == '__main__' :
    main()
    