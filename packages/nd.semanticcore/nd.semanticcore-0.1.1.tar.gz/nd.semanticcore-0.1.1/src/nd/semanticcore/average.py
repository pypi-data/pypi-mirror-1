### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertor text to vector of features

$Id: average.py 51799 2008-09-29 20:36:12Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51799 $"

from math import log
from text2vector import Text2Vector

class Average(object) : 

    def __init__(self) :
        pass            

    def __call__(self,vectors) :
        self.vectors = tuple(vectors)[:]
        self.set = set()
        for vector in self.vectors :
            self.set.update(set(vector))
            
        self.dictionary = {}            

        sq = 0
        for word in self.set :
            W = sum((v.get(word,0) for v in self.vectors)) / float(len(self.vectors))
            #S = float(sum(( (v.has_key(word) and 1 or 0) for v in self.vectors)))
            sq += W ** 2
            self.dictionary[word] = W
            
        sq = sq ** 0.5
        return dict([ (x,float(y)/sq) for x,y in self.dictionary.items()]) 


if __name__ == '__main__' :
    import os,sys
    from text2vector import Text2Vector
    average = Average()((Text2Vector()(open(x).read()) for x in sys.argv[1:] ))
    for name,value in sorted(average.items(), lambda x,y : cmp(x[1],y[1])) :
        print "%-20s" % name, value
        