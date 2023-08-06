### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to present lazy decorator for fuction

$Id: lazy.py 51059 2008-05-04 15:12:44Z cray $
"""
__author__  = "Andrey Orlov, 20008"
__license__ = "GPL"
__version__ = "$Revision: 51059 $"

def _(s) : return s

class Method(object) :
    def __init__(self,lazy,inst,cache) :
        self.lazy = lazy 
        self.inst = inst
        self.cache = cache
        
    def __call__(self,*kv,**kw) :
        index = (tuple(kv),(tuple(kw.items())))
        try :
            data = self.cache[index]
        except KeyError :
            data = self.cache[index] = self.lazy.func(self.inst,*kv,**kw)
            
        return data            
        
class Lazy(object):
    """Lazy Attributes
    """

    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.cache = {}

    def __get__(self, inst, class_):
        if inst is None:
            return self
        cache = self.cache.setdefault(id(inst),{}).setdefault(self.name,{})
        return Method(self,inst,cache)

    
class A(object) : 
   @Lazy
   def a(self,a,b,c,d=1,e=1) :
    #print a,b,c,d,e
    #print "self",self
    return a,b,c,d,e
    
 
    