### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to insert soft hyphen sign in russian words.

$Id: hyphen.py 52725 2009-03-27 15:53:42Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52725 $"

def _(s) : return s

import re
match = re.compile(u"(?<!\s)[аеёиоуыюя](?!\s)",re.U|re.X)
match = re.compile(u"(?<!^)(?<!\s)[аеёиоуыюя](?!(\w{,1}(\s|$)))",re.U|re.X)

            
def hyphen(x) :
    return re.sub(match,lambda x : x.group()+"&shy;",x)
