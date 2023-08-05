### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module content different utilities

$Id: utility.py 13545 2007-12-10 00:56:30Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 13545 $"

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
    


