#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find provides in python sources

$Id: provides.py 12907 2007-11-10 17:26:55Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12900 $"

def _(s) : return s

import sys, os
prefix = "python%u.%u" % sys.version_info[0:2]


def file_provides(files,frm=lambda x : "%s(%s)" % (prefix,x)) :
        
    path = []
    for item in [ [x for x in [ x.strip() for x in open(x).readlines() ] if x] for x in files if os.path.splitext(x) == ".pth" and os.path.dirname(x) == os.path.join('usr','lib',prefix,'site-packages') ] :
        path.extend(item)

    path = tuple(sys.path[1:])+tuple(os.getenv('RPM_PYTHON_LIB_PATH','').split()) + tuple(path)
    
    pl = [] 
    buildroot = os.getenv('RPM_BUILD_ROOT',"")
    
    init_d = dict(
        [(x,None) for x,y in [ os.path.split(x) for x in files ] if y == '__init__.py']
        + [ (os.path.normpath(buildroot + "/" + x),None) for x in os.getenv('RPM_PYTHON_MODULE_DECLARED','').split() ]
    )


    for module in os.getenv('RPM_PYTHON_MODULE_DECLARED','').split() :
    
        module = [ x for x in module.split("/") if x]
        
        for item in path :
        
            item = [ x for x in item.split("/") if x]
            
            if item == module[0:len(item)] :
                root = os.path.normpath(buildroot + "/" + os.path.join(*item))
                
                for parent in module[len(item):] :
                    root = os.path.join(root,parent)
                    if not init_d.has_key(root) :
                        break
                else :
                    pl.append( ( (".".join(module[len(item):]),) ,os.path.join(* ["/",buildroot]+module) ))

    path = [os.path.normpath(os.path.join( buildroot or '/', './'+x)) for x in path  ]

    sd = {}

    for src in files :
        if os.path.normpath(os.path.dirname(src)) in path :
            m,e = os.path.splitext( os.path.basename(src))
            if not '/' in m :
                yield (frm(m),src)
                
                if e in ['.so'] :
                    if m[-6:] == "module" :
                        yield (frm(m[0:-6]),src)

        if os.path.basename(src) in ['__init__.py'] :
            if os.path.dirname(os.path.dirname(src)) in path :
                pl.append(((os.path.basename(os.path.dirname(src)),), os.path.dirname(src)) )
                yield (frm(os.path.basename(os.path.dirname(src))),src)

        name,ext = os.path.splitext(os.path.basename(src))
        if ext in [".py"] :
            if name not in [ "__init__" ]:
                sd.setdefault(os.path.dirname(src),[]).append(name)
            else :
                sd.setdefault(os.path.dirname(os.path.dirname(src)),[]).append(os.path.basename(os.path.dirname(src)))


    while pl :
        m,p = pl.pop()

        try :
            pis = sd[p]
        except KeyError :
            pass
        else :
            for pi in pis :
                mo = m+(pi,)
                yield (frm(".".join(mo)),pi)
                pl.insert(0,(mo, os.path.join(p,pi)))

def main() :
    import sys
    for item in file_provides(sys.argv[1:]) :
        print item


if __name__ == '__main__' :
    main()