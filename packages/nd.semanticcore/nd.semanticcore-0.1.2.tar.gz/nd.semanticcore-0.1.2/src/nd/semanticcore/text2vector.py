### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The convertor text to vector of features

$Id: text2vector.py 51838 2008-10-09 21:05:34Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51838 $"

import re

class Text2Vector(object) :
    __doc__ = __doc__

    reword = re.compile(u'\w+',re.U)

    def __init__(self,reword=u'\w+'):
        self.reword = re.compile(reword,re.U)
         
    def __call__(self,text) :
        return self.normAndVector(text)[1]
            
    def normAndVector(self,text) :
        d = {}
        
        try :
            text = unicode(text)
        except UnicodeDecodeError :            
            return 0,{}
        else :            
            for word in re.findall(self.reword,text) :
                word = word.lower()
                try :
                    d[word] += 1      
                except KeyError :
                    d[word] = 1
            
            sq = 0                
            for value in d.values() :
                sq += value ** 2
                
            sq = float(sq) ** 0.5      
            
            return sq,dict([ (x,float(y)/sq) for x,y in d.items()]) 
                    

if __name__ == '__main__' :
    import os,sys
    for name in sys.argv :
        print name, Text2Vector()(open(name).read())
        