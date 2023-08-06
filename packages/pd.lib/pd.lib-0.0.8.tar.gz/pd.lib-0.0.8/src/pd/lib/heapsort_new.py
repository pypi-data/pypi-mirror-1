### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to sort in lazy fashion by means of heapq.

$Id: heapsort_new.py 49591 2007-12-22 01:43:28Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 49591 $"

def _(s) : return s

import heapq

class HeapSort(object) :
    def __init__(self,l,f) :
        class A(object) :
            def __init__(self,ob) :
                self.ob=ob
                
            def __cmp__(self,x) :
                return f(self.ob,x.ob)
        self.A = A                
                
        self.l = [A(x) for x in l]
        heapq.heapify(self.l)
       
    def chunk(self,x=1) :
        for n in range(0,x) :
            yield heapq.heappop(self.l).ob
            
    def pop(self) :
        return self.chunk().next()
                    
    def expand(self,l) :
        for item in l :
            self.push(item)
            
    def push(self,item) :
        heapq.heappush(self.l,self.A(item))
                                 
    def __len__(self) :
        return len(self.l)
        
    def view(self) :
        return self.l[-1].ob        

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


