### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to find greatest common divisor

$Id: gcd.py 51892 2008-10-21 08:28:59Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51892 $"

def _(s) : return s

def gcd(a,b) :
    c = a % b	
    if c == 0 :
        return b
    else :
        return gcd(b,c)

