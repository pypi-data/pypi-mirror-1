### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to sort in lazy fashion by means of heapq.

$Id: heapsort.py 13545 2007-12-10 00:56:30Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 13545 $"

def _(s) : return s

import heapq

class HeapSort(object) :
    def __init__(self,l,f) :
        class A(object) :
            def __init__(self,ob) :
                self.ob=ob
                
            def __cmp__(self,x) :
                return f(self.ob,x.ob)
        self.l = [A(x) for x in l]
        heapq.heapify(self.l)
       
    def chunk(self,x) :
        for n in range(0,x) :
            yield heapq.heappop(self.l).ob

class HeapSortByIndex(HeapSort) :
    def __init__(self,l,i,revert = False) :
        super(HeapSortByIndex,self).__init__(l,
            revert and (lambda x,y : cmp(i[y],i[x])) or (lambda x,y : cmp(i[x],i[y]))
            )

class HeapSortByIndexSafe(HeapSort) :
    def __init__(self,l,i,revert = False) :
        def safecmp(x,y) :
            try :
                ix = i[x]
            except KeyError :
                return 1

            try :
                iy = i[y]
            except KeyError :
                return -1

            return cmp(ix,iy)
                                
        super(HeapSortByIndexSafe,self).__init__(l,
            revert and (lambda x,y : safecmp(y,x)) or safecmp
            )


