### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Topological sorting alogrithms realized in OOP

$Id: topsort.py 49594 2007-12-22 04:57:02Z cray $
"""
__author__  = ""
__license__ = "ZPL"
__version__ = "$Revision: 49594 $"
__date__ = "$Date: 2007-12-22 07:57:02 +0300 (Сбт, 22 Дек 2007) $"
__creadits__ = "Anatoly Zaretsky"

from heapsort import HeapSort as HeapQueue

class SortIsNotPossible(Exception):
    pass

class UnknownDependency(KeyError):
    pass

class _Node(object):

    def __init__(self):
        self.refs = 0
        self.adjacent = set()

class Queue([].__class__) :
    def push(self,x) :
        super(Queue,self).insert(0,x)

class TopSortBase(object) :

    def __init__(self,reversed=False) :
        self.reversed = reversed 
        
    def initroots(self,elements) :        
        self.graph = dict((obj, _Node()) for obj, _unused in elements)
        for obj, deps in elements:
            for dep in deps:
                if self.reversed:
                    _from, _to = dep, obj
                else:
                    _from, _to = obj, dep
                try:
                    _from_adj = self.graph[_from].adjacent
                    if _to not in _from_adj:
                        _from_adj.add(_to)
                        self.graph[_to].refs += 1
                except KeyError:
                    raise UnknownDependency, "Unknown dependency %s of %s" % (dep, obj)

        self.roots = Queue([(obj, node) for obj, node in self.graph.iteritems() if node.refs == 0])                
        
    def sort(self) :
        while self.roots:
            obj, node = self.roots.pop()
            del self.graph[obj]
            yield obj

            for next in node.adjacent :
                next_node = self.graph[next]
                next_node.refs -= 1
                if next_node.refs == 0:
                    self.roots.push((next, next_node))

    def __call__(self,elements) :
        self.initroots(elements)
        for item in self.sort() :
            yield item
        if self.graph:
            raise SortIsNotPossible(self.graph.keys())

class TopSortFuzzyBase(object) :
    def sort(self) :
        while True :
            for item in super(TopSortFuzzyBase,self).sort() :
                yield item

            if self.graph :
                it = self.graph.iteritems()
                min = it.next()[0]
                for obj, node in list(it) :
                    if self.graph[min].refs > node.refs :
                        min = obj
                node = self.graph[min]
                print "------>",min,node.refs
                for item in node.adjacent :
                    print "=", item
                node.refs = 0
                self.roots.push((min,node))                                                           

                for obj,node in self.graph.iteritems() :
                    if min in node.adjacent :
                        print obj
                        node.adjacent.remove(min)
            else :
                break                                                    
                    
class TopSortIndexBase(object) :
    def __call__(self,elements) :
        d = {}
        for obj, deps in elements :
            d[id(obj)] = obj
            for dep in deps :
                d[id(dep)] = dep
        return (d[id] for id in super(TopSortIndexBase,self).__call__([(id(obj),[id(dep) for dep in deps]) for obj,deps in elements]))            


class TopSortFuzzy(TopSortFuzzyBase, TopSortBase) :
    pass

class TopSortFuzzyIndex(TopSortIndexBase,TopSortFuzzyBase, TopSortBase) :
    pass

class TopSort(TopSortBase) :
    pass

class TopSortIndex(TopSortIndexBase, TopSortBase) :
    pass

