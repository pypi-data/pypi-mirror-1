#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find requires in python sources

$Id: requires.py 12907 2007-11-10 17:26:55Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 12900 $"

def _(s) : return s

import sys, os
import parser, symbol, token, types

prefix = "python%u.%u" % sys.version_info[0:2]

def getReqName(x) :
    return "%s(%s)" % (prefix,x)

symbol_skip = [symbol.encoding_decl, symbol.classdef]

# Preliminary hack to python 2.4 compatibility
def pro(x) :
    return x[1]
            
ignore = dict([ (x,1) for x in 
    list(os.getenv('RPM_PYTHON_REQ_SKIP',"").split())
    + list(sys.builtin_module_names)]).has_key

REQ = os.getenv('RPM_PYTHON_REQ_METHOD','relaxed')
IS_HIER = os.getenv('RPM_PYTHON_REQ_HIER','hier')

def match(tree,deep=0) :
    if tree[0] not in  symbol_skip :
        deep += 1
    for node in tree :
        if type(node) in [types.ListType, types.TupleType] :
            if node[0] == symbol.import_stmt :
                if REQ not in ['slight','relaxed'] or deep == 4 :
                    node = pro(node)
                    if node[1][1] == 'import' :
                        for name in [x for x in node[2][1:] if x[0] != 12  ] :
                            if IS_HIER is None :
                                yield name[1][1][1]
                            else :
                                yield ".".join( [ i for t,i in  name[1][1:] if t==1 ])

                    elif node[1][1] == 'from' :
                        if IS_HIER is None :
                            yield node[2][1][1]
                        else :
                            yield ".".join( [ i for t,i in  node[2][1:] if t==1 ])
         
            for item in match(node,deep) :
                yield item

def requires(src,frm=getReqName) :
    try :
        lis = parser.suite(file(src).read().rstrip().replace("\r\n","\n")).tolist()
    except SyntaxError,msg :
        pass
    else :
        for item in match(lis) :
            if not ignore(item) :
                yield frm(item)

def file_requires(files) :
    for src in files :
        if '.py' == os.path.splitext(os.path.basename(src))[1] :
            for item in requires(src) :
                yield (item,src)

def main() :
    for item in file_requires(sys.argv[1:]) :
        print item
    return 1        

if __name__ == '__main__' :
    import sys
    sys.exit(main)            
