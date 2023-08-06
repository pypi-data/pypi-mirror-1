Short module description
=========================

Module pd.lib content some simple modules
and fucntions.

Description of modules
----------------------

pd.lib.heapsort
...............

The module is simple lazy sort implementation realised therewith heapq
module. Items will be sorted only when accepted and using of computation
resource is minimazed.

Two classes are provided by module:

    HeapSort
        On initialization accepted item list and comparing
        function;
        
    HeapSortByIndex
        On initialization accepted item list and index.  List
        items mapped on index values and can be compared by them. In this
        case third parameter - revert - are used.  Revert can be True or
        False. If revert is True then array will be sorted in reverse order.
        Parameter revert is False by default.

    HeapSortByIndexSafe
        It class liked on HeapSortByIndex above, but use index in extremely safe
        manner: if item omited from index it mapped on infinity and any item are 
        comparable;

Classes, mentioned above, to provide methods:

    chunk(n)
        Return first n items from begin sorted list.

pd.lib.utility
..............

The module contents followed useful functions:
        
    name2klass
        Return klass by name
        
    klass2name
        Return name by klass

                                
pd.lib.topsort
..............

The module contents classes developed to provide different kind of topologic
sort. All classes are use as:

    TopSort([<Parameters>])(<Items>), где :
    
    Parameters
        Sort execution parameters;
        
    Items
        Each item is a pair of object reference and object reference list which one depend;
        
Followed classes are provided by module:

    TopSort
        Simple topologic sort;
        
    TopSortIndex
        Simple topologic sort for any kind of object;

    TopSortFuzzy
        Fuzzy topologic sort;
        
    TopSortFuzzyIndex
        Fuzzy topologic sort for any kind of object;
        

Fuzzy topologic sort can transform to linear ordered array graph with
cyclomatic value more then zero. Best results achieved on litle values: the
sort is for tree with a few cycles.

pd.lib.lazy
...........
The module contents **Lazy** decorator class used to cache return value on
methods depend on argumetnts. Be carryfully, method arguments are to be
hashable.


Sample of use:

    >>> from pd.lib.lazy import Lazy
    >>>
    >>> class A(object) :
    ...     @Lazy
    ...     def mul(self,a,b) :
    ...         print a,b,"compute"
    ...         return a*b
    ...
    >>> a=A() a.mul(1,2)
    1 2 compute 2
    >>> a.mul(2,3) 2 3 compute 6
    >>> a.mul(1,2) 2 a.mul(2,3) 6
    >>>          

Using such version of **lazy** decorator get processes incredible speed, but
more memory will be used.


pd.lib.fuzzyobject
..................

The module provide FuzzyObject class. Inheritance from FuzzyObject to allow
forget about typografic errors in class names::

    >>> from pd.lib.fuzzyobject import FuzzyObject class A(FuzzyObject) :
    ...     def commmon_function(self) :
    ...         print 'common'
    ...     def other_method(self) :
    ...         print 'method'
    ...
    >>> A().coon_functi() common A().oth_m() method
    >>        

This base class is toy, but it's worked. More complicated sample published
in pd/lib/fuzzyobject/fuzzyobject_sample.py, some pro and contra of such
programming are viewed from.

Conclusion 
----------- 

Main target of this product to carry all small, frequently used libraries.
This library must be installed on use other our products by depend. But I
think product have not got independent significance.
