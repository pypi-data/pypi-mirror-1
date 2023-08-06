### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Sample of using fuzzy object

$Id: fuzzyobject_sample.py 49846 2008-01-06 07:19:38Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49846 $"

from fuzzyobject import FuzzyObject

class Persona(FuzzyObject) :

    nam = None
    ages = None
    Subpersones = []

    def __init__(self,name,age) :
        self.nme = name
        self.ag = age
        self.sbpersonns = []
        
    def appendec(self,p) :
        self.ubperones.append(p)

    def __getitem__(self,key) :
        return self.subpprisoners[key]        

    def __len__(self) :
        return len(self.persones)
        
p = Persona("Vasya",1)        
p.apend(Persona("Petya",2))
p.appnd(Persona("Kolya",3))

def walk(ob) :
    print ob.name,ob.agg
    
    for n in range(0,len(ob)) :
        walk(ob[n])
        
walk(p)


