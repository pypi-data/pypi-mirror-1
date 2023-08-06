### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007                                                                 #
#######################################################################
"""TreeNode comparing routines

$Id: treenodeklp.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from ks.lib.treenodeklp import logger

class CompareError(Exception):
    pass

class TreeNodeKLP(object):
    """Tree Node Compare Class"""

    def __init__(self, parent, children, check):
        self.parent = parent
        self.children = children
        self.check = check

    def __call__(self, node1, node2):
        first = self.getPath(node1)
        second = self.getPath(node2)
        logger.debug('First: %s', first)
        logger.debug('Second: %s', second)
        k = 0
        while k < min(len(first), len(second)) \
              and first[k] == second[k]:
            k += 1
        if k < len(first) and k < len(second):
            children = list(self.children(first[k-1]))
            logger.debug('Cross Node Children: %s', children)
            logger.debug('First Index: %s, Second Index: %s', children.index(first[k]), children.index(second[k]))
            return cmp(children.index(second[k]), children.index(first[k]))
        else:
            logger.debug('Nodes in one Leaf')
            return cmp(len(second), len(first))

    def getPath(self, node):
        nodes = []
        while node is not None and self.check(node):
            nodes.append(node)
            node = self.parent(node)
        nodes.reverse()
        return nodes

