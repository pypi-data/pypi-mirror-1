#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This script developed to do some dependence
analysys in python sources

$Id: imalyzer.py 12907 2007-11-10 17:26:55Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12900 $"

def _(s) : return s

import sys,os
from pd import find
from requires import requires,getReqName 

def check(*paths) :
    common_files = reduce(lambda x,y : x|y,
        [ set([z.path for z in x]) for x in 
            [find.find(y,lambda x : x.isreg() and x.check_regex(".*.py$"), lambda x : x.isreg() or x.isdir() and x.has_key("__init__.py")) for y in paths]
        ])

    common_files_with = reduce(lambda x,y : x|y,
        [ set([z.path for z in x]) for x in 
            [find.find(y,lambda x : x.isreg() and x.check_regex(".*.py$")) for y in paths]
        ])

    files = set([ x.path for x in [find.File(y) for y in paths] if x.isreg() and x.check_regex(".*.py$")])
    files |= set([ x["__init__.py"].path for x in [find.File(y) for y in paths] if x.isdir() and x.has_key("__init__.py") ])
    
    check_files = set(())
    callable_files = files.copy()
    external = {}

    ss = common_files_with-common_files
    
    if ss :
        print   " ============= \n" \
                "   This modules are lost: \n" \
                " ------------ "
                
        for item in sorted(ss) :
            print "\t",item


    print   " ============= \n" \
            "   List of callable modules:\n" \
            " ------------ "

    for item in sorted(files) :
        print "\t",item


    print   " ============= \n" \
            "   Links between modules:\n" \
            " ------------ "

    while files :
        fn = files.pop()
        try :
            for req in list(set(requires(fn,frm=lambda x : x))) :
                req = os.path.join(*req.split("."))
                for pth in (os.path.dirname(fn),) + tuple(set([os.path.dirname(x) for x in paths])) + tuple(sys.path) :
                    for item in ["%s.py","%s.pyc","%s.so","%smodule.so","%s/__init__.py"] :
                        pitem = os.path.join(pth,item % req) 
                        if pitem in common_files :
                            print "\t",fn,"->",pitem
                            if pitem not in check_files and pitem != fn :
                                files|=set([pitem])
                            check_files|=set([pitem])
                            break
                    else :
                        continue
                    break                            
                else :
                    external.setdefault(req,[]).append(fn)
                    
                            
        except IOError,msg :
            print fn,msg
            pass

    if check_files :
        print   " ============= \n" \
                "   This modules are used:\n" \
                " ------------ "

        for item in sorted(check_files) :
            print "\t",item


    ss = common_files-check_files-callable_files
    if ss:
        print   " ============= \n" \
                "   This modules are not used by self:\n" \
                " ------------ "

        for item in sorted(ss) :
            print "\t",item
        
        print   " ============= \n" \

    if external :
        print   " ============= \n" \
                "   External requires:\n" \
                " ------------ ",

        for req,modules in sorted(external.items()) :
            print "\n\t",getReqName(req)
            for module in modules :
                print "\t\t",module
        
    print   " ============= \n" \

def main() :
    check(*sys.argv[1:])

            
if __name__ == '__main__' :
    main()
    