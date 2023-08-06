### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertor text to vector of features

$Id: vectorcompare.py 51799 2008-09-29 20:36:12Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51799 $"

import re
from text2vector import Text2Vector


def vectorcompare(v1,v2) :
    v3 = {}
    for key in set(v1.keys()+v2.keys()) :
        v3[key] = v1.get(key,0) - v2.get(key,0)

    return sorted(v3.items(),lambda (x1,y1),(x2,y2) : cmp(y2,y1))

if __name__ == '__main__' :
    import os,sys

    for key,value in vectorcompare( Text2Vector()(open(sys.argv[1]).read()), Text2Vector()(open(sys.argv[2]).read()) ) :
        print "%-40s:" % key,value
        