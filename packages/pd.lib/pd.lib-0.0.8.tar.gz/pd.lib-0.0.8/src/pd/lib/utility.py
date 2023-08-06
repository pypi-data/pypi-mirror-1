### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module content different utilities

$Id: utility.py 14154 2007-12-09 20:22:23Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 14154 $"

def _(s) : return s

def name2klass(name) :
    try :
        pos = name.rindex(".")
        module = name[0:pos]
        klass = name[pos+1:]
        return getattr(__import__(module,globals(),locals(),[klass]),klass)
    except Exception, msg:
        print msg
        return None        

def klass2name(klass) :
    return klass.__module__ + "." + klass.__name__
    


