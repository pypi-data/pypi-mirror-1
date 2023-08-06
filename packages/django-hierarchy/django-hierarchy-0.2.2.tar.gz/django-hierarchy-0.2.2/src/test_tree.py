# -*- coding: utf-8 -*-
# 
#  test_tree.py
#  django-hierarchy
#  
#  Created by Lars Yencken on 2009-04-09.
#  Copyright 2009 Lars Yencken. All rights reserved.
# 

import unittest
from tree import TreeNode

#----------------------------------------------------------------------------#

def suite():
    testSuite = unittest.TestSuite((
            unittest.makeSuite(TreeTestCase),
        ))
    return testSuite

#----------------------------------------------------------------------------#

class TreeTestCase(unittest.TestCase):
    """This class tests the Tree class."""

    def setUp(self):
        root = TreeNode('fruit')
        root.add_child(TreeNode('lemon'))
        root.add_child(TreeNode('strawberry'))
        self.fruit = root
        pass

    def testWalkPreorder(self):
        nodes = [n for n in self.fruit.walk()]
        self.assertEqual(nodes[0], self.fruit)
        self.assertEqual(nodes[1], self.fruit.children['lemon'])
        self.assertEqual(nodes[2], self.fruit.children['strawberry'])
        pass
    
    def testWalkPostorder(self):
        nodes = [n for n in self.fruit.walk_postorder()]
        self.assertEqual(nodes[0], self.fruit.children['lemon'])
        self.assertEqual(nodes[1], self.fruit.children['strawberry'])
        self.assertEqual(nodes[2], self.fruit)
        pass

    def testWalkMptt(self):
        nodes = [n for n in self.fruit.walk_mptt()]
        self.assertEqual(nodes[0], (self.fruit, False))
        self.assertEqual(nodes[1], (self.fruit.children['lemon'], False))
        self.assertEqual(nodes[2], (self.fruit.children['lemon'], True))
        self.assertEqual(nodes[3], (self.fruit.children['strawberry'], False))
        self.assertEqual(nodes[4], (self.fruit.children['strawberry'], True))
        self.assertEqual(nodes[5], (self.fruit, True))

    def testPrune(self):
        x = self.fruit.copy().prune(lambda n: 'y' not in n.label)
        self.assertEqual(x.label, 'fruit')
        self.assertEqual(x.children.values(), [self.fruit.children['lemon']])

    def testWalkLeaves(self):
        orange = TreeNode('orange')
        self.fruit.children['lemon'].add_child(orange)
        strawberry = self.fruit.children['strawberry']
        self.assertEqual([orange, strawberry],
                list(sorted(self.fruit.walk_leaves())))

    def tearDown(self):
        pass

#----------------------------------------------------------------------------#

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(suite())

#----------------------------------------------------------------------------#

# vim: ts=4 sw=4 sts=4 et tw=78:

