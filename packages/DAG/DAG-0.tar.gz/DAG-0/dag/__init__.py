#Copyright (c) 2006 Simon Wittber
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation files
#(the "Software"), to deal in the Software without restriction,
#including without limitation the rights to use, copy, modify, merge,
#publish, distribute, sublicense, and/or sell copies of the Software,
#and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""
dag.py implements a simple directed acyclic graph structure, and provides a
simple traversal function which takes a callback argument.
"""

import weakref
from collections import deque


class Node(object):
    """
    A node in a graph.
    """
    _instances = weakref.WeakValueDictionary()
    _instance_count = 0
    def __new__(cls, *args, **kw):
        instance = object.__new__(cls, *args, **kw)
        instance._id = Node._instance_count
        Node._instances[instance._id] = instance
        Node._instance_count += 1
        return instance

    @classmethod
    def get(cls, id):
        """
        Returns a node by its _id attribute.
        """
        return cls._instances[id]

    def __repr__(self):
        return "<%s #%s object>" % (self.__class__.__name__, self._id)


class Composite(Node):
    """
    A node in a graph, composed of other nodes.
    """
    def __init__(self, *children):
        self.children = list(children)

    def add(self, *nodes):
        self.children.extend(nodes)

    def remove(self, *nodes):
        for i in nodes:
            self.children.remove(i)


def traverse(root, dispatch):
    """
    Traverse down the tree, processing nodes from left to right, calling dispatch on each node.
    """
    stack = deque([root])
    stack_pop = stack.popleft
    stack_extend = stack.extend
    stack_rotate = stack.rotate
    while stack:
        node = stack_pop() 
        dispatch(node)
        if hasattr(node, 'children'):
            stack_extend(node.children)
            stack_rotate(len(node.children))


if __name__ == "__main__":  
    import unittest

    class TestDAGClasses(unittest.TestCase):
        def setUp(self):
            self.root_node = Composite()
            self.leaf_a = Composite()
            self.leaf_b = Node()
            self.root_node.add(self.leaf_a, self.leaf_b)

        def testAddComposite(self):
            self.root_node.add(Composite())
            self.assert_(len(self.root_node.children) == 3)

        def testGetMethod(self):
            self.assert_(Node.get(self.leaf_a._id) is self.leaf_a)

        def testRemove(self):
            self.root_node.remove(self.leaf_a, self.leaf_b)
            self.assert_(self.leaf_a not in self.root_node.children)
            self.assert_(self.leaf_b not in self.root_node.children)

        def testOrdering(self):
            self.root_node.add(self.leaf_b, self.leaf_a)
            self.assert_(self.root_node.children[-1] is self.leaf_a)

        def testTraverse(self):
            processing_order = []

            def callback(node):
                processing_order.append(node)

            leaf_c = Node()
            self.leaf_a.add(leaf_c)
            traverse(self.root_node, callback)
            self.assert_(processing_order == [self.root_node, self.leaf_a, leaf_c, self.leaf_b])

    unittest.main()



         

