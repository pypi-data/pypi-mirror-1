### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""test class for the treenodeklp package

$Id: test_compare.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

import unittest
from ks.lib.treenodeklp import TreeNodeKLP
import logging

class TestNode(list):

    def __init__(self, title, parent=None):
        self.__parent__ = parent
        if parent is not None:
            parent.append(self)
        self.title = title

    def __repr__(self):
        return '<TreeNode %s>' % (self.title)

class CompareTestCase(unittest.TestCase):
    """Base Class"""

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

        self.klp = TreeNodeKLP(lambda x: x.__parent__,
                               lambda x: list(x),
                               lambda x: True)

    def tearDown(self):
        pass

    def testCompareOtherLeaves(self):
        r1 = TestNode('r1')
        r2 = TestNode('r2', r1)
        r3 = TestNode('r3', r2)
        r4 = TestNode('r4', r1)
        self.assertEqual(self.klp(r3, r4), 1)

    def testCompareOneLeave(self):
        r1 = TestNode('r1')
        r2 = TestNode('r2', r1)
        r3 = TestNode('r3', r2)
        r4 = TestNode('r4', r1)
        self.assertEqual(self.klp(r3, r2), -1)

if __name__ == '__main__':
    unittest.main()