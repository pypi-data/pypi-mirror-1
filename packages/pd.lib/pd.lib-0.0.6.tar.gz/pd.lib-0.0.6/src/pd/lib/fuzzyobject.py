### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module content fuzzy object

$Id: fuzzyobject.py 49846 2008-01-06 07:19:38Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49846 $"

import difflib

class FuzzyObject(object) :
    
    __fuzzy_attribute_cache__ = {}
    
    def __getattr__(self, attr) :
        return getattr(self,self.__fuzzy_search__(attr))
    
    def __setattr__(self, attr, value) :
        if attr not in dir(self) :
            try :
                attr = self.__fuzzy_search__(attr)  
            except AttributeError,msg :
                pass
                
        super(FuzzyObject,self).__setattr__(attr, value)                            
                                
    def __fuzzy_search__(self, attr) :
        try :
            return self.__fuzzy_attribute_cache__[attr]
        except KeyError :
            imax = 0.5
            nmax = None

            if attr in ['__members__','__methods__'] :
                raise AttributeError

            for key in dir(self)[:] :
                i = difflib.SequenceMatcher(None,attr,key).ratio()
                if i >= imax :
                    imax = i
                    nmax = key

            if nmax :
                self.__fuzzy_attribute_cache__[attr] = nmax
                return nmax
            
        raise AttributeError,attr                        
    
        

