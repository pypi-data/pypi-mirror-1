### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007                                                                 #
#######################################################################
"""Topological sorting routines

$Id: topolsort.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"


class SortIsNotPossible(Exception):
    pass


class UnknownDependency(KeyError):
    pass


class _Node(object):

    def __init__(self):
        self.refs = 0
        self.adjacent = set()


def baseTopSort(elements, reversed=True):
    graph = dict((obj, _Node()) for obj, _unused in elements)
    for obj, deps in elements:
        for dep in deps:
            if reversed:
                _from, _to = dep, obj
            else:
                _from, _to = obj, dep
            try:
                _from_adj = graph[_from].adjacent
                if _to not in _from_adj:
                    _from_adj.add(_to)
                    graph[_to].refs += 1
            except KeyError:
                raise UnknownDependency, "Unknown dependency %s of %s" % (dep, obj)
    roots = [(obj, node) for obj, node in graph.iteritems() if node.refs == 0]
    while roots:
        obj, node = roots.pop()
        del graph[obj]
        yield obj
        for next in node.adjacent:
            next_node = graph[next]
            next_node.refs -= 1
            if next_node.refs == 0:
                roots.append((next, next_node))
    if graph:
        raise SortIsNotPossible(graph.keys())


def topSort(elements, *args, **kw):
    d = dict(((obj.name, obj) for obj in elements))
    def find_dep(obj, dep_name):
        dep = d.get(dep_name)
        if dep is None:
            raise UnknownDependency, "Unknown dependency %s of %s" % (dep_name, obj.name)
        return dep
    return baseTopSort([(obj, [find_dep(obj, name)
                               for name in obj.requires])
                        for obj in elements],
                       *args, **kw)
