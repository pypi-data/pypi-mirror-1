dm.iter
=======

A small collection of iterator utilities.

Currently, there is a single utility family related to relations.


Relation utilities
------------------

These utilies are implemented in ``dm.iter.relation``.

The relation is represented by a map from an element to an
iterator of its directly related elements.
The map is either an object with ``__getitem__`` method,
a callable raising ``ValueError`` for undefined
input arguments or an object supporting subscription.
Elements must be allowed as set elements.

Available utilies are ``depth_first_search`` and ``breath_first_search``.
They take as arguments a relation and an element iterator ''roots''
and generate the relation's transitive closure for ''roots''
in depth first or breath first order, respectively.

Lets look at a trivial example. Our relation has the integers between
0 and 11 as domain and maps an element to three times this element.

>>> def relation(x):
...   if not (isinstance(x, int) and 0 <= x < 11): raise ValueError
...   return (3 * x,)
...
>>> from dm.iter.relation import depth_first_search, breadth_first_search
>>> tuple(depth_first_search(relation, ()))
()
>>> tuple(breadth_first_search(relation, ()))
()
>>> tuple(depth_first_search(relation, (1, 2, 3)))
(1, 3, 9, 27, 2, 6, 18)
>>> tuple(breadth_first_search(relation, (1, 2, 3)))
(1, 2, 3, 6, 9, 18, 27)
>>> dfs = depth_first_search(relation, (1, 2, 3))
>>> dfs.next()
1
>>> dfs.next()
3

We now let our relation map ``x`` to ``(2*x, 3*x)``.

>>> def relation(x):
...   if not (isinstance(x, int) and 0 <= x < 11): raise ValueError
...   return (2 * x, 3 * x)
...
>>> tuple(depth_first_search(relation, (1,)))
(1, 2, 4, 8, 16, 24, 12, 6, 18, 3, 9, 27)
>>> tuple(breadth_first_search(relation, (1,)))
(1, 2, 3, 4, 6, 9, 8, 12, 18, 27, 16, 24)

The relation can also be specified by a dictionary.

>>> relation = dict((i, (2*i, 3*i)) for i in range(11))
>>> tuple(depth_first_search(relation, (1,)))
(1, 2, 4, 8, 16, 24, 12, 6, 18, 3, 9, 27)
>>> tuple(breadth_first_search(relation, (1,)))
(1, 2, 3, 4, 6, 9, 8, 12, 18, 27, 16, 24)

Or an object with ``__getitem__`` method:

>>> from UserDict import UserDict
>>> relation = UserDict(relation)
>>> tuple(depth_first_search(relation, (1,)))
(1, 2, 4, 8, 16, 24, 12, 6, 18, 3, 9, 27)
>>> tuple(breadth_first_search(relation, (1,)))
(1, 2, 3, 4, 6, 9, 8, 12, 18, 27, 16, 24)
