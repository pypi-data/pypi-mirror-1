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

        
        
                
