# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------#
# This file is part of Py-gtktree.                                         #
#                                                                          #
# Copyright (C) 2009 Paul Pogonyshev.                                      #
#                                                                          #
# This program is free software: you can redistribute it and/or modify it  #
# under the terms of the GNU Lesser General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or (at    #
# your option) any later version.                                          #
#                                                                          #
# This program is distributed in the hope that it will be useful, but      #
# WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser #
# General Public License for more details.                                 #
#                                                                          #
# You should have received a copy of the GNU Lesser General Public License #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#--------------------------------------------------------------------------#


if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))


import unittest

import gtk

from test._common  import Foo, PopAllList
from gtktree.model import RowObjectTreeStore, TreeNode, DefaultTreeNode



# Some tests assume current order of row changing, insertion, removal or reordering (when
# sorting).  Such tests will fail if this order is changed for whatever reason and those
# failures won't necessary indicate real bugs.  In that case, you will need to check and
# possibly alter these tests.

class RowObjectTreeStoreTestCase (unittest.TestCase):

    def test_create (self):
        # No shortcut here.
        store = RowObjectTreeStore ([(int, 'foo')])
        self.assert_(isinstance (store, RowObjectTreeStore))


    def test_create_with_values (self):
        store, emissions = _create_foo_tree_store ()
        self.assertEqual (store.root.num_child_nodes, 2)


    def test_sortable_interface_1 (self):
        store, emissions = _create_sorting_foo_tree_store (already_sorted = False)

        self.assert_(not store.is_sorted)

        store.set_sort_column_id (0, gtk.SORT_ASCENDING)
        self.assert_     (store.is_sorted)
        self.assertEqual (store.root.build_row_object_skeleton () [1:],
                          _sorting_foo_forest_sorted_ascending ())
        self.assertEqual (emissions.pop_all (),
                          [('reordered',         '?' or [0, 1, 2]),
                           ('reordered', (0,),   '?' or [3, 4, 1, 2, 0]),
                           ('reordered', (0, 3), '?' or [0, 1]),
                           ('reordered', (1,),   '?' or [1, 0])])

        store.set_sort_column_id (0, gtk.SORT_DESCENDING)
        self.assert_     (store.is_sorted)
        self.assertEqual (store.root.build_row_object_skeleton () [1:],
                          _sorting_foo_forest_sorted_descending ())
        self.assertEqual (emissions.pop_all (),
                          [('reordered',         '?' or [2, 1, 0]),
                           ('reordered', (2,),   '?' or [4, 3, 2, 1, 0]),
                           ('reordered', (2, 1), '?' or [1, 0]),
                           ('reordered', (1,),   '?' or [1, 0])])


    # Test that it 'appends' at the correct position.
    def test_sortable_interface_append (self):
        store, emissions = _create_sorting_foo_tree_store ()
        node             = store.root

        node.child_nodes.append (DefaultTreeNode (Foo (2.5)))
        self.assertEqual (node.child_nodes[2].row_object, Foo (2.5))
        self.assertEqual (emissions.pop_all (), [('inserted', (2,))])


    def test_sortable_interface_set_row_object (self):
        store, emissions = _create_sorting_foo_tree_store ()
        node             = store.root.child_nodes[0].child_nodes[2]

        node.row_object = Foo (10.5)

        self.assertEqual (node.parent_node.child_row_objects,
                          [Foo (10), Foo (10.5), Foo (11), Foo (13), Foo (14)])
        self.assertEqual (emissions.pop_all (), [('changed', (0, 2)),
                                                 ('reordered', (0,), '?' or [0, 2, 1, 3, 4])])


    def test_sortable_interface_note_changes (self):
        store, emissions = _create_sorting_foo_tree_store ()
        node             = store.root.child_nodes[2]

        node.row_object.foo = 0.5
        store.note_changes (node)

        self.assertEqual (node.parent_node.child_row_objects, [Foo (0.5), Foo (1), Foo (2)])
        self.assertEqual (emissions.pop_all (), [('changed', (2,)),
                                                 ('reordered', '?' or [2, 0, 1])])



class TreeNodeTestCase (unittest.TestCase):

    _TREE_1 = DefaultTreeNode.create_tree ([1,
                                            [2,
                                             [3,
                                              [4],
                                              [5]],
                                             [6]],
                                            [7],
                                            [8,
                                             [9,
                                              [10],
                                              [11]],
                                             [12]]])


    def test_depth_first_order_trivial (self):
        self._do_trivial_test (TreeNode.depth_first_order)

    def test_depth_first_order_1 (self):
        tree = self._TREE_1
        self.assertEqual (self._get_order_list (tree.depth_first_order ()),
                          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual (self._get_order_list (tree.depth_first_order (False)),
                          [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])


    def test_traversal_postorder_trivial (self):
        self._do_trivial_test (TreeNode.traversal_postorder)

    def test_traversal_postorder_1 (self):
        tree = self._TREE_1
        self.assertEqual (self._get_order_list (tree.traversal_postorder ()),
                          [4, 5, 3, 6, 2, 7, 10, 11, 9, 12, 8, 1])
        self.assertEqual (self._get_order_list (tree.traversal_postorder (False)),
                          [4, 5, 3, 6, 2, 7, 10, 11, 9, 12, 8])


    def test_breadth_first_order_trivial (self):
        self._do_trivial_test (TreeNode.breadth_first_order)

    def test_breadth_first_order_1 (self):
        tree = self._TREE_1
        self.assertEqual (self._get_order_list (tree.breadth_first_order ()),
                          [1, 2, 7, 8, 3, 6, 9, 12, 4, 5, 10, 11])
        self.assertEqual (self._get_order_list (tree.breadth_first_order (False)),
                          [2, 7, 8, 3, 6, 9, 12, 4, 5, 10, 11])


    def _do_trivial_test (self, order_factory):
        node = DefaultTreeNode (1)
        self.assertEqual (self._get_order_list (order_factory (node)),
                          [1])
        self.assertEqual (self._get_order_list (order_factory (node, False)),
                          [])

        # Assert that presence of parent and next node doesn't modify returned sequence.

        parent = DefaultTreeNode (0, [node])
        self.assertEqual (self._get_order_list (order_factory (node)),
                          [1])
        self.assertEqual (self._get_order_list (order_factory (node, False)),
                          [])

        parent.child_nodes.append (DefaultTreeNode (2))
        self.assertEqual (self._get_order_list (order_factory (node)),
                          [1])
        self.assertEqual (self._get_order_list (order_factory (node, False)),
                          [])


    @staticmethod
    def _get_order_list (order):
        row_objects = []
        for node in order:
            row_objects.append (node.row_object)

        return row_objects



class DefaultTreeNodeTestCase (unittest.TestCase):

    def test_set_item_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        node.child_nodes[0] = DefaultTreeNode (Foo (50))
        self.assertEqual (node.num_child_nodes, 2)
        self.assertEqual (node.child_nodes[0].row_object, Foo (50))
        self.assertEqual (emissions.pop_all (), [('deleted', (0,)),
                                                 ('inserted', (0,))])

    def test_set_slice_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        node.child_nodes[-2:2] = [DefaultTreeNode (Foo (30))]
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (node.child_nodes[0].row_object, Foo (30))
        self.assertEqual (emissions.pop_all (), [('deleted', (1,)),
                                                 ('deleted', (0,)),
                                                 ('inserted', (0,))])


    def test_delete_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        del node.child_nodes[0]
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (emissions.pop_all (), [('deleted', (0,))])

    def test_delete_2 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        del node.child_nodes[-1]
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (emissions.pop_all (), [('deleted', (1,))])

    def test_delete_slice_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        del node.child_nodes[:]
        self.assert_(not node.has_child_nodes)
        self.assertEqual (emissions.pop_all (), [('deleted', (1,)),
                                                 ('deleted', (0,))])


    # Appending to root.
    def test_append_1 (self):
        store, emissions = _create_foo_tree_store (())
        node             = store.root

        node.child_nodes.append (DefaultTreeNode (Foo (10)))
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (node.child_nodes[0].row_object, Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,))])

        node.child_nodes.append (DefaultTreeNode (Foo (20)))
        self.assertEqual (node.num_child_nodes, 2)
        self.assertEqual (node.child_nodes[1].row_object, Foo (20))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,))])

    # Appending to a pre-existing node.
    def test_append_2 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root.child_nodes[0]

        node.child_nodes.append (DefaultTreeNode (Foo (10)))
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (node.child_nodes[0].row_object, Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0, 0))])

        node.child_nodes.append (DefaultTreeNode (Foo (20)))
        self.assertEqual (node.num_child_nodes, 2)
        self.assertEqual (node.child_nodes[1].row_object, Foo (20))
        self.assertEqual (emissions.pop_all (), [('inserted', (0, 1))])

    # Appending to a pre-existing level 2 node.
    def test_append_3 (self):
        store, emissions = _create_foo_tree_store (
            [DefaultTreeNode (Foo (0)),
             DefaultTreeNode (Foo (10),
                              [DefaultTreeNode (Foo (20))])])

        node = store.root.child_nodes[1].child_nodes[0]

        node.child_nodes.append (DefaultTreeNode (Foo (30)))
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (node.child_nodes[0].row_object, Foo (30))
        self.assertEqual (emissions.pop_all (), [('inserted', (1, 0, 0))])

        node.child_nodes.append (DefaultTreeNode (Foo (40)))
        self.assertEqual (node.num_child_nodes, 2)
        self.assertEqual (node.child_nodes[1].row_object, Foo (40))
        self.assertEqual (emissions.pop_all (), [('inserted', (1, 0, 1))])


    def test_append_subtree (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root.child_nodes[1]

        node.child_nodes.append (DefaultTreeNode (Foo (10),
                                                  [DefaultTreeNode (Foo (20))]))
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (node.child_nodes[0].row_object, Foo (10))
        self.assertEqual (node.child_nodes[0].child_nodes[0].row_object, Foo (20))
        self.assertEqual (emissions.pop_all (), [('inserted', (1, 0))])


    def test_extend_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        node.child_nodes.extend (DefaultTreeNode (Foo (30 + k)) for k in range (3))
        self.assertEqual (node.num_child_nodes, 5)
        self.assertEqual (node.child_nodes[2].row_object, Foo (30))
        self.assertEqual (node.child_nodes[3].row_object, Foo (31))
        self.assertEqual (node.child_nodes[4].row_object, Foo (32))
        self.assertEqual (emissions.pop_all (), [('inserted', (2,)),
                                                 ('inserted', (3,)),
                                                 ('inserted', (4,))])


    def test_insert_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        node.child_nodes.insert (0, DefaultTreeNode (Foo (100)))
        self.assertEqual (node.num_child_nodes, 3)
        self.assertEqual (node.child_nodes[0].row_object, Foo (100))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,))])

    def test_insert_2 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        node.child_nodes.insert (-1, DefaultTreeNode (Foo (50)))
        self.assertEqual (node.num_child_nodes, 3)
        self.assertEqual (node.child_nodes[1].row_object, Foo (50))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,))])


    def test_remove_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        node.child_nodes.remove (node.child_nodes[0])
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (emissions.pop_all (), [('deleted', (0,))])

        node.child_nodes.remove (node.child_nodes[0])
        self.assertEqual (node.num_child_nodes, 0)
        self.assertEqual (emissions.pop_all (), [('deleted', (0,))])

    def test_remove_2 (self):
        store, emissions = _create_foo_tree_store (
            [DefaultTreeNode (Foo (0)),
             DefaultTreeNode (Foo (10),
                              [DefaultTreeNode (Foo (20)),
                               DefaultTreeNode (Foo (30))])])

        node = store.root.child_nodes[1]

        node.child_nodes.remove (node.child_nodes[1])
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (emissions.pop_all (), [('deleted', (1, 1))])

        node.child_nodes.remove (node.child_nodes[0])
        self.assertEqual (node.num_child_nodes, 0)
        self.assertEqual (emissions.pop_all (), [('deleted', (1, 0))])


    def test_pop_1 (self):
        store, emissions = _create_foo_tree_store ()
        node             = store.root

        popped = node.child_nodes.pop ()
        self.assertEqual (popped.row_object, Foo (2, 'abc'))
        self.assertEqual (node.num_child_nodes, 1)
        self.assertEqual (emissions.pop_all (), [('deleted', (1,))])


    def test_illegal_child_1 (self):
        self.assertRaises (TypeError, lambda: DefaultTreeNode ().child_nodes.append ('foo'))

    def test_illegal_child_2 (self):
        x = DefaultTreeNode (None, [DefaultTreeNode (None)])
        y = DefaultTreeNode (None)
        self.assertRaises (ValueError, lambda: y.child_nodes.append (x.first_child_node))

    def test_illegal_child_3 (self):
        store, emissions = _create_foo_tree_store (())
        self.assertRaises (ValueError, lambda: DefaultTreeNode ().child_nodes.append (store.root))

    def test_illegal_child_4 (self):
        x = DefaultTreeNode (None)
        self.assertRaises (ValueError, lambda: x.child_nodes.append (x))

    def test_illegal_child_5 (self):
        x = DefaultTreeNode.create_tree ([None, [None]])
        self.assertRaises (ValueError, lambda: x.child_nodes[0].child_nodes.append (x))
        


def _create_foo_tree_store (nodes = None):
    if nodes is None:
        nodes = [DefaultTreeNode (Foo (1)), DefaultTreeNode (Foo (2, 'abc'))]

    store     = RowObjectTreeStore ([(int, 'foo'),
                                     (str, 'bar')],
                                    nodes)
    emissions = PopAllList ()

    store.connect ('row-changed',
                   lambda model, path, iter:
                       emissions.append (('changed', path)))
    store.connect ('row-deleted',
                   lambda model, path:
                       emissions.append (('deleted', path)))
    store.connect ('row-inserted',
                   lambda model, path, iter:
                       emissions.append (('inserted', path)))

    def reordered (model, path, iter, new_order):
        if not path and iter is None:
            # 'new_order' is not readable in Python (it is gobject.GPointer)...
            emissions.append (('reordered', '?'))
        else:
            emissions.append (('reordered', path, '?'))

    store.connect ('rows-reordered', reordered)

    return store, emissions



def _sorting_foo_forest ():
    return [[Foo (1),
             [Foo (14)],
             [Foo (12),
              [Foo (120)]],
             [Foo (13),
              [Foo (130)],
              [Foo (131)]],
             [Foo (10)],
             [Foo (11)]],
            [Foo (3)],
            [Foo (2),
             [Foo (21)],
             [Foo (20)]]]

def _sorting_foo_forest_sorted_ascending ():
    return [[Foo (1),
             [Foo (10)],
             [Foo (11)],
             [Foo (12),
              [Foo (120)]],
             [Foo (13),
              [Foo (130)],
              [Foo (131)]],
             [Foo (14)]],
            [Foo (2),
             [Foo (20)],
             [Foo (21)]],
            [Foo (3)]]

def _sorting_foo_forest_sorted_descending ():
    return [[Foo (3)],
            [Foo (2),
             [Foo (21)],
             [Foo (20)]],
            [Foo (1),
             [Foo (14)],
             [Foo (13),
              [Foo (131)],
              [Foo (130)]],
             [Foo (12),
              [Foo (120)]],
             [Foo (11)],
             [Foo (10)]]]

def _create_sorting_foo_tree_store (values = None, already_sorted = True):
    if values is None:
        values = DefaultTreeNode.create_forest (*_sorting_foo_forest ())

    store, emissions = _create_foo_tree_store (values)

    if already_sorted:
        store.set_sort_column_id (0, gtk.SORT_ASCENDING)
        emissions.pop_all ()

    return store, emissions



if __name__ == '__main__':
    unittest.main ()



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
