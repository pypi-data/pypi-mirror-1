### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertor text to vector of features

$Id: tfidf.py 51799 2008-09-29 20:36:12Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51799 $"

from math import log
from text2vector import Text2Vector

class TFIDF(object) : 

    def __init__(self,vectors) :
        self.vectors = tuple(vectors)[:]
            

    def __call__(self) :
        self.set = set()
        for vector in self.vectors :
            self.set.update(set(vector))
            
        self.dictionary = {}            

        for word in self.set :
            #S = sum((v.get(word,0) for v in self.vectors)) 
            S = float(sum(( (v.has_key(word) and 1 or 0) for v in self.vectors)))

            print word,S
            self.dictionary[word] = 0

            for v in self.vectors :
                try :
                    p = v[word]
                except KeyError :
                    pass
                else :   
                    print "--",p,S
                    try :                                     
                        #v[word] = e = p * log(p/S) 
                        v[word] = e = p * log(S/len(self.vectors))
                    except ZeroDivisionError :
                        print "Zero:", word
                    else :                                        
                        self.dictionary[word] = log(S/len(self.vectors)) * S / len(self.vectors)
                    
        return self.dictionary

if __name__ == '__main__' :
    import os,sys
    from text2vector import Text2Vector
    tfidf = TFIDF((Text2Vector()(open(x).read()) for x in sys.argv[1:] ))
    for name,value in sorted(tfidf().items(), lambda x,y : cmp(x[1],y[1])) :
        print "%-20s" % name, value
        