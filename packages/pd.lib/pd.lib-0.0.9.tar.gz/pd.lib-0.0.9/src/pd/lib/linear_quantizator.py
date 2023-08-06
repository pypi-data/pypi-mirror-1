### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to compute the best linear quantization and
mapping quants to linear oredered labels

$Id: linear_quantizator.py 52856 2009-04-07 14:09:54Z cray $
"""
__author__  = "Andrey Orlov, 20008"
__license__ = "GPL"
__version__ = "$Revision: 52856 $"


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

    #print "d:",d
    #print "init:",positions
    prev = 0
    for x in range(0,1000) :
        dpos = dict(((x,[]) for x in positions))
        for key in d :
            m = mx - mn
            for position in positions :
                sub = abs(position - d[key][1])
                if sub <= m :
                    m = sub
                    pos = position
                    
            dpos.setdefault(pos,[]).append(key) 

        #print "dpo",[x for x in sorted(dpos)]
        p = sorted([ len(dpos[x]) and sum([d[key][1] for key in dpos[x]]) / len(dpos[x])  for x in dpos ])
        positions = [(0.98*p[0]+0.02*p[1])]
        #print "pre",p
        for i in range(1,len(p)-1) :
            positions.append(p[i-1]*0.02+p[i]*0.96+p[i+1]*0.02)

        #print p[i],p[i+1]            
        positions.append(0.98*p[i+1]+0.02*p[i])


        res = sum([ sum([ (d[key][1]-y)**2 for key in dpos[x] ])   for x,y in zip(dpos,positions)])
        #print "pos",positions
        #print "res",res
        if abs(res - prev) < 0.01 :
            break
        prev = res            
                    

    l = []
    #print "key",sorted(dpos.keys())
    
    for y,ids in zip(positions,[ y for x,y in sorted(dpos.items())] ) :
        for id in ids :
            l.append((d[id][0],y) )

    #print "L1:",l            
    return l            
    
    
def round(quants,num) :
    """ For sequence pairs (label, value) return the best mapping on pairs
    (label, value), where value is integer in [0,num] """
    weights = list(set([y for x,y in quants]))    
    mn = min(weights)
    mx = max(weights)
    k = float(num) / float(mx-mn)
    return [ (x, int((y-mn)*k) ) for x,y in quants] 

def elastic(quants,num) :        
    l = sorted(list(set((y for x,y in quants ))))    
    u = num / float(len(l))
    w = int((num - int((len(l)-1) * u))/2.)
    d = dict([ (x,int(y*u)+w) for x,y in zip(l,range(0,len(l))) ])
    return [ (x,d[y]) for x,y in quants ]

    
if __name__ == '__main__' :
    import random
    
    q = quantizator(
            [ (lambda x : (x,x))(random.random()*10) for ch in "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+="],
            5
            )
            
    for x,y in sorted(q) :
        print x,y

    print "-------"                    
    for x,y in  sorted(list(round([(x,y) for x,y in q],20))):
        print x,y            
