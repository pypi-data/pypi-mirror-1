# Copyright (C) 2010 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Eppelborn, Germany
# see "LICENSE.txt" for details

class Undefined(Exception):
  """Exception indicating an element outside the relations domain."""


def depth_first_search(rel, roots):
  """generate transitive closure of *roots* (an iterator) wrt *rel* in depth first order."""
  return _search(rel, roots, -1)


def breadth_first_search(rel, roots):
  """generate transitive closure of *roots* (an iterator) wrt *rel* in breath first order."""
  return _search(rel, roots, 0)


def _search(rel, roots, index):
  rel = _normalize_relation(rel)
  seen = set()
  work = [iter(roots)]
  while work:
    w = work[index]
    try: e = w.next()
    except StopIteration: work.pop(index); continue
    if e in seen: continue
    seen.add(e)
    yield e
    try: directly_related = rel(e)
    except Undefined: continue
    work.append(iter(directly_related))


def _normalize_relation(rel):
  """*rel* can be:

    * an object with '__getitem__'
    
    * a callable raising 'ValueError' to indicate an out of domain value
    
    * an object supporting subscription

  They are mapped to a function raising 'Undefined' to indicate an out of
  domain value
  """
  ga = getattr(rel, '__getattr__', None)
  if ga is not None: f, exc = ga, KeyError
  elif callable(rel): f, exc = rel, ValueError
  else: f, exc = lambda x: rel[x], KeyError
  def wrapped(x):
    try: return f(x)
    except exc: raise Undefined()
  return wrapped
