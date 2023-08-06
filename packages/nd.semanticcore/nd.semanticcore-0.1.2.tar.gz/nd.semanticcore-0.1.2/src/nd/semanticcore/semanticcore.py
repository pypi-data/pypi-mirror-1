#!/usr/bin/python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Script treat two corpus of text to find semantic core
by them.

Used:
    semanticcore [<OPIONS>] <SAMPLE1> <DELIMETER> <SAMPLE2>
    
Sample:
    <SAMPLE1>, <SAMPLE2> is eneumeration of text files. Sample1 is target
    sampling for tags (keywords) definition. Sample2 is control samping ...
    
Switch:

    -d  <STRING>        Delimeter (default :::);
    
    -w  <INT>:<INT>     Weight interval to display (default 0:10);  

    -c  <INT>           Lowest border number of word in document used to except 
                        words (default 10);

$Id: semanticcore.py 53462 2009-07-13 12:55:37Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53462 $"

import sys, os, getopt
from cloudcompare import CloudCompare


def main() :
    isverbose = False
    delim = ":::"
    wmin = 0
    wmax = 10
    dcmin = 10


    opts,fns = getopt.getopt(sys.argv[1:],"vd:w:c:") 


    if not fns :
        print __doc__
        sys.exit(0)        

    for opt,val in opts :
        if opt in ["-v"] :
            isverbose = True
        elif opt in ["-d"] :
            delim = val
        elif opt in ["-w"] :
            wmin,wmax = [ int(x) for x in val.split(":") ]
        elif opt in ["-c"] :
            dcmin = int(val)
        else :
            print >>sys.stderr, "Unknown switch %s" % opt
            sys.exit(1)
            
    border = fns.index(delim)
    cc = CloudCompare(dcmin=dcmin)

    for name,value,w1,w2 in cc((open(x).read() for x in fns[:border]),(open(y).read() for y in fns[border+1:]) ) :
        if wmin <= w1 < wmax :
            print "%-20s" % name, value, w1, w2
            
    return 0

if __name__ == '__main__' :
    sys.exit(main())
            