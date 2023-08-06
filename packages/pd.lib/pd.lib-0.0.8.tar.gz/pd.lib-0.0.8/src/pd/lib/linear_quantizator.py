### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to compute the best linear quantization and
mapping quants to linear oredered labels

$Id: linear_quantizator.py 52574 2009-02-12 07:23:13Z cray $
"""
__author__  = "Andrey Orlov, 20008"
__license__ = "GPL"
__version__ = "$Revision: 52574 $"


def quantizator(quants,n) :
    """ Evaluate samples of some labeled values (label, value) and return
    sequence pairs (label, value) where value are quantized by n levels """
    
    d = dict(zip(range(0,len(quants)),quants))
    weights = [y for x,y in quants ]
    mn = min(weights)
    mx = max(weights)

    step = float(mx - mn) / float(n)
    positions = [mn]
    for x in range(0,n) :
        positions.append(positions[-1]+step)

    prev = 0
    for x in range(0,10) :
        dpos = {}
        for key in d :
            m = mx - mn
            for position in positions :
                sub = abs(position - d[key][1])
                if sub <= m :
                    m = sub
                    pos = position
                    
            dpos.setdefault(pos,[]).append(key) 

        positions = [ sum([d[key][1] for key in dpos[x]]) / len(dpos[x])  for x in dpos ]                     
        #positions = [(0.98*p[0]+0.002*p[1])]
        #for i in range(1,len(p)-1) :
        #    positions.append(p[i-1]*0.002+p[i]*0.96+p[i+1]*0.002)
        #    
        #positions.append(0.98*p[i]+0.002*p[i-1])


        res = sum([ sum([ (d[key][1]-y)**2 for key in dpos[x] ])   for x,y in zip(dpos,positions)])
        print "pos",positions
        print "res",res
        if abs(res - prev) < 0.01 :
            break
        prev = res            
                    

    l = []
    for ids, y in zip(dpos.values(),positions) :
        for id in ids :
            l.append((d[id][0],y) )

    #print "L1:",l            
    return l            
    
def mapper(quants,num) :    
    """ For sequence pairs (label, value) return the best mapping on pairs
    (label, value), where value is integer in [0,num] """

    ns = range(0,num)

    weights = sorted(list(set([y for x,y in quants ])))

    mn = min(weights)
    mx = max(weights)

    if mx == mn :
        print mx,mn
        return [(x,int(num/2)) for x,y in quants]
    else :
        k = num / (mx - mn)
        print k, num, mx, mn
        ws = [ (x-mn)*k for x in weights ]
        print ws, weights, ns
        if len(ns) > len(ws) :
            l = []
            for n in ns :
                mw = ws[0]
                mn = abs(n-mw)

                for w in ws[1:]:
                    mnc = abs(n - w)
                    if mnc < mn :        
                        mw = w
                        mn = mnc 
                l.append((mn,n))
            ns = sorted([ y for x,y in sorted(l)[0:len(ws)]])
                    
        print ns
        d = dict(zip(weights,ns))
        l = [ (x,d[y]) for x,y in quants ]        
        print "L2",l
        return l
    
if __name__ == '__main__' :
    import random
    
    q = quantization(
            [ (lambda x : (x,x))(random.random()*10) for ch in "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+="],
            5
            )
            
    for x,y in sorted(q) :
        print x,y
                    
    for x,y in  sorted(list(mapping([(x,y) for x,y in q],20))):
        print x,y            
