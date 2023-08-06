### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertor text to vector of features

$Id: cloudcompare.py 53516 2009-07-25 07:23:59Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53516 $"

from math import log
from text2vector import Text2Vector
from vectorcompare import vectorcompare
from average import Average

class CloudCompare(object) :
    def __init__(self,dcmin = 10) :
        self.dcmin = dcmin
        
    def __call__(self,vs1,vs2) :
        v1 = [ (sq,v) for sq,v in [(Text2Vector().normAndVector(x)) for x in vs1 ] if sq > 0 ]
        v2 = [ (sq,v) for sq,v in [(Text2Vector().normAndVector(x)) for x in vs2 ] if sq > 0 ]
        av1 = Average()([ x[1] for x in v1])
        av2 = Average()([ x[1] for x in v2])
        d1 = {}
        d2 = {}

        for av,d,v in (av1,d1,v1), (av2,d2,v2) :
            count = 0
            
            for (sq,vector) in v :
                count += 1
                dcmin = float(self.dcmin)/sq
                for word, weight in vector.items() :
                    #print word, "==", weight, dcmin, weight * sq 
                    #word, weight, weight * len(vector) 
                    if weight > dcmin : # weight * len(vector) > self.dcmin :
                        try :
                            d[word] += 1
                        except KeyError :
                            d[word] = 1

            for word in d :
                try :
                    d[word] = min(100,1+int(count / 100. * float(d[word])))
                except KeyError :
                    print word                    
                    
        return ( (x,y,d1.get(x,0),d2.get(x,0)) for x,y in  vectorcompare(av1,av2) if x in d1 or x in d2)
           
if __name__ == '__main__' :
    import os,sys
    delim = sys.argv.index(":::")
    
    for name,value,w1,w2 in CloudCompare()((open(x).read() for x in sys.argv[1:delim]),(open(y).read() for y in sys.argv[delim+1:]) ) :
        if 0 < w1 <= 10 :
            print "%-20s" % name, value, w1, w2
         