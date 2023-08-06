### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to sort in lazy fashion by means of heapq.

$Id: heapsort.py 49788 2008-01-03 21:09:38Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49788 $"

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
            try :
                yield heapq.heappop(self.l).ob
            except IndexError :
                break
                                

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


