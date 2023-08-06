# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------#
# This file is part of Py-gtktree.                                         #
#                                                                          #
# Copyright (C) 2008, 2009 Paul Pogonyshev.                                #
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

from test._common  import Foo, PopAllList
from gtktree.model import RowObjectListStore



# Some tests assume current order of row changing, insertion or removal.  Such tests will
# fail if this order is changed for whatever reason and those failures won't necessary
# indicate real bugs.  In that case, you will need to check and possibly alter these
# tests.
#
# Currently assumed orders:
# - row changing: first to last;
# - row insertion: first to last;
# - row deletion: last to first.
#
# In slice assignment it is additionally assumed that as far as possible model emits
# 'row-changed' signal.  If the numbers of old and new rows differ, additional
# 'row-inserted' or 'row-deleted' signals are emitted after that.

class RowObjectListStoreTestCase (unittest.TestCase):

    def test_create (self):
        # No shortcut here.
        store = RowObjectListStore ([(int, 'foo')])
        self.assert_(isinstance (store, RowObjectListStore))


    def test_create_with_values (self):
        store, emissions = _create_foo_list_store ()
        self.assertEqual (len (store), 2)


    def test_get_item (self):
        store, emissions = _create_foo_list_store ()

        self.assertEqual (store[0], Foo (1))
        self.assertEqual (store[1], Foo (2, 'abc'))
        self.assertEqual (store[0:2], [Foo (1), Foo (2, 'abc')])


    def test_get_value (self):
        store, emissions = _create_foo_list_store ()

        row = store.get_iter_first ()
        self.assertEqual (store.get_value (row, 0), 1)
        self.assertEqual (store.get_value (row, 1), None)

        row = store.iter_next (row)
        self.assertEqual (store.get_value (row, 0), 2)
        self.assertEqual (store.get_value (row, 1), 'abc')


    def test_get_cell (self):
        store, emissions = _create_foo_list_store ()

        self.assertEqual (store.get_cell (0, 'foo'), 1)
        self.assertEqual (store.get_cell (0, 'bar'), None)
        self.assertEqual (store.get_cell (1, 'foo'), 2)
        self.assertEqual (store.get_cell (1, 'bar'), 'abc')


    def test_set_item (self):
        store, emissions = _create_foo_list_store ()

        store[0] = Foo (10)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (emissions.pop_all (), [('changed', (0,), 0)])

        store[1] = Foo (20)
        self.assertEqual (store[1], Foo (20))
        self.assertEqual (emissions.pop_all (), [('changed', (1,), 1)])

        store[-1] = Foo (30)
        self.assertEqual (store[1], Foo (30))
        self.assertEqual (emissions.pop_all (), [('changed', (1,), 1)])

        def set (index, value):
            store[index] = value

        self.assertRaises (IndexError, lambda: set (2,  Foo (40)))
        self.assertRaises (IndexError, lambda: set (-3, Foo (40)))
        self.assertEqual  (emissions.pop_all (), [])


    def test_set_slice (self):
        store, emissions = _create_foo_list_store ()

        store[1:1] = (Foo (10), Foo (20))
        self.assertEqual (len (store), 4)
        self.assertEqual (store[1], Foo (10))
        self.assertEqual (store[2], Foo (20))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,), 1),
                                                 ('inserted', (2,), 2)])

        store[1:2] = (Foo (30), Foo (40))
        self.assertEqual (len (store), 5)
        self.assertEqual (store[1], Foo (30))
        self.assertEqual (store[2], Foo (40))
        self.assertEqual (store[3], Foo (20))
        self.assertEqual (emissions.pop_all (), [('changed',  (1,), 1),
                                                 ('inserted', (2,), 2)])

        store[-4:-1] = (Foo (50),)
        self.assertEqual (len (store), 3)
        self.assertEqual (store[1], Foo (50))
        self.assertEqual (emissions.pop_all (), [('changed',  (1,), 1),
                                                 ('deleted',  (3,)),
                                                 ('deleted',  (2,))])


    def test_set_extended_slice (self):
        store, emissions = _create_foo_list_store (Foo (index) for index in range (10))

        store[1:8:3] = Foo (-1), Foo (-2), Foo (-3)
        self.assertEqual (len (store), 10)
        self.assertEqual (store[1], Foo (-1))
        self.assertEqual (store[4], Foo (-2))
        self.assertEqual (store[7], Foo (-3))
        self.assertEqual (emissions.pop_all (), [('changed', (1,), 1),
                                                 ('changed', (4,), 4),
                                                 ('changed', (7,), 7)])

        def set (slice, value):
            store[slice] = value

        self.assertRaises (ValueError, lambda: set (slice (1, 8, 3), [Foo (100)]))


    def test_append (self):
        store, emissions = _create_foo_list_store ([])

        store.append (Foo (10))
        self.assertEqual (len (store), 1)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,), 0)])

        store.append (Foo (20))
        self.assertEqual (len (store), 2)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (store[1], Foo (20))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,), 1)])


    def test_prepend (self):
        store, emissions = _create_foo_list_store ([])

        store.prepend (Foo (10))
        self.assertEqual (len (store), 1)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,), 0)])

        store.prepend (Foo (20))
        self.assertEqual (len (store), 2)
        self.assertEqual (store[0], Foo (20))
        self.assertEqual (store[1], Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,), 0)])


    def test_insert (self):
        store, emissions = _create_foo_list_store ([])

        store.insert (0, Foo (10))
        self.assertEqual (len (store), 1)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,), 0)])

        store.insert (0, Foo (20))
        self.assertEqual (len (store), 2)
        self.assertEqual (store[0], Foo (20))
        self.assertEqual (store[1], Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,), 0)])

        store.insert (1, Foo (30))
        self.assertEqual (len (store), 3)
        self.assertEqual (store[0], Foo (20))
        self.assertEqual (store[1], Foo (30))
        self.assertEqual (store[2], Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,), 1)])


    def test_insert_after (self):
        store, emissions = _create_foo_list_store ([])

        store.insert_after (0, Foo (10))
        self.assertEqual (len (store), 1)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (emissions.pop_all (), [('inserted', (0,), 0)])

        store.insert_after (0, Foo (20))
        self.assertEqual (len (store), 2)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (store[1], Foo (20))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,), 1)])

        store.insert_after (0, Foo (30))
        self.assertEqual (len (store), 3)
        self.assertEqual (store[0], Foo (10))
        self.assertEqual (store[1], Foo (30))
        self.assertEqual (store[2], Foo (20))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,), 1)])


    def test_insert_negative_position (self):
        store, emissions = _create_foo_list_store ([Foo (0), Foo (1), Foo (2)])

        store.insert (-2, Foo (10))
        self.assertEqual (len (store), 4)
        self.assertEqual (store[:], [Foo (0), Foo (10), Foo (1), Foo (2)])
        self.assertEqual (emissions.pop_all (), [('inserted', (1,), 1)])


    def test_insert_out_of_bounds (self):
        store, emissions = _create_foo_list_store ([Foo (0), Foo (1), Foo (2)])

        # As with Python lists, we expect out-of-bounds positions be silently clamped.
        store.insert (100, Foo (100))
        self.assertEqual (len (store), 4)
        self.assertEqual (store[:], [Foo (0), Foo (1), Foo (2), Foo (100)])
        self.assertEqual (emissions.pop_all (), [('inserted', (3,), 3)])

        store.insert (-100, Foo (-100))
        self.assertEqual (len (store), 5)
        self.assertEqual (store[:], [Foo (-100), Foo (0), Foo (1), Foo (2), Foo (100)])
        self.assertEqual (emissions.pop_all (), [('inserted', (0,), 0)])


    def test_extend (self):
        store, emissions = _create_foo_list_store ([Foo (0)])

        store.extend ([Foo (10), Foo (20), Foo (30)])
        self.assertEqual (len (store), 4)
        self.assertEqual (store[0], Foo (0))
        self.assertEqual (store[1], Foo (10))
        self.assertEqual (store[2], Foo (20))
        self.assertEqual (store[3], Foo (30))
        self.assertEqual (emissions.pop_all (), [('inserted', (1,), 1),
                                                 ('inserted', (2,), 2),
                                                 ('inserted', (3,), 3)])


    def test_remove (self):
        store, emissions = _create_foo_list_store ([Foo (1), Foo (2), Foo (3), Foo (4)])

        store.remove (Foo (3))
        self.assertEqual (len (store), 3)
        self.assertEqual (store[0], Foo (1))
        self.assertEqual (store[1], Foo (2))
        self.assertEqual (store[2], Foo (4))
        self.assertEqual (emissions.pop_all (), [('deleted', (2,))])

        store, emissions = _create_foo_list_store ([Foo (1), Foo (2), Foo (3), Foo (4),
                                                         Foo (3), Foo (2), Foo (1)])
        store.remove (Foo (3))
        self.assertEqual (len (store), 6)
        self.assertEqual (store[3], Foo (3))
        self.assertEqual (emissions.pop_all (), [('deleted', (2,))])

        store.remove (Foo (3))
        self.assertEqual (len (store), 5)
        self.assertEqual (emissions.pop_all (), [('deleted', (3,))])
        self.assertRaises (ValueError, lambda: store.index (Foo (3)))

        self.assertRaises (ValueError, lambda: store.remove (Foo (3)))


    def test_pop (self):
        store, emissions = _create_foo_list_store ([Foo (1), Foo (2), Foo (3), Foo (4)])

        popped = store.pop ()
        self.assertEqual (len (store), 3)
        self.assertEqual (store[0], Foo (1))
        self.assertEqual (store[1], Foo (2))
        self.assertEqual (store[2], Foo (3))
        self.assertEqual (popped, Foo (4))
        self.assertEqual (emissions.pop_all (), [('deleted', (3,))])

        popped = store.pop (0)
        self.assertEqual (len (store), 2)
        self.assertEqual (store[0], Foo (2))
        self.assertEqual (store[1], Foo (3))
        self.assertEqual (popped, Foo (1))
        self.assertEqual (emissions.pop_all (), [('deleted', (0,))])


    def test_clear (self):
        store, emissions = _create_foo_list_store ()
        self.assert_(len (store) == 2)

        store.clear ()
        self.assertEqual (len (store), 0)
        self.assertEqual (emissions.pop_all (), [('deleted', (1,)),
                                                 ('deleted', (0,))])


    def test_reverse (self):
        store, emissions = _create_foo_list_store ()

        contents = store[:]

        store.reverse ()
        self.assertEqual (store[:], list (reversed (contents)))
        self.assertEqual (emissions.pop_all (),
                          [('reordered', '?' or list (reversed (range (len (contents)))))])


    # Note: we don't use Foo() here to simplify things.  We don't access columns anyway,
    # so this doesn't matter.
    def test_sort (self):
        store, emissions = _create_foo_list_store (['C', 'e', 'b', 'A', 'D'])
        store.sort ()
        self.assertEqual (store[:], ['A', 'C', 'D', 'b', 'e'])
        self.assertEqual (emissions.pop_all (), [('reordered', '?' or [1, 4, 3, 0, 2])])

        store, emissions = _create_foo_list_store (['C', 'e', 'b', 'A', 'D'])
        store.sort (key = str.lower)
        self.assertEqual (store[:], ['A', 'b', 'C', 'D', 'e'])
        self.assertEqual (emissions.pop_all (), [('reordered', '?' or [2, 4, 1, 0, 3])])

        store, emissions = _create_foo_list_store (['C', 'e', 'b', 'A', 'D'])
        store.sort (cmp = lambda a, b: -cmp (a, b))
        self.assertEqual (store[:], ['e', 'b', 'D', 'C', 'A'])
        self.assertEqual (emissions.pop_all (), [('reordered', '?' or [2, 0, 3, 4, 1])])

        store, emissions = _create_foo_list_store (['C', 'e', 'b', 'A', 'D'])
        store.sort (cmp = lambda a, b: -cmp (a, b), key = str.lower)
        self.assertEqual (store[:], ['e', 'D', 'C', 'b', 'A'])
        self.assertEqual (emissions.pop_all (), [('reordered', '?' or [3, 0, 1, 4, 2])])

        store, emissions = _create_foo_list_store (['C', 'e', 'b', 'A', 'D'])
        store.sort (reverse = True)
        self.assertEqual (store[:], ['e', 'b', 'D', 'C', 'A'])
        self.assertEqual (emissions.pop_all (), [('reordered', '?' or [2, 0, 3, 4, 1])])


    def test_swap (self):
        store, emissions = _create_foo_list_store ([Foo (0), Foo (1), Foo (2), Foo (3)])

        store.swap (1, 3)
        self.assertEqual (store[1], Foo (3))
        self.assertEqual (store[3], Foo (1))
        self.assertEqual (emissions.pop_all (), [('reordered', '?' or [0, 3, 2, 1])])


    # Note: we don't use Foo() in the move_* tests to simplify things.  We don't access
    # columns anyway, so this doesn't matter.

    def test_move_to (self):
        self._do_test_move (lambda store: store.move_to (2, 0),
                            [2, 0, 1, 3, 4])
        self._do_test_move (lambda store: store.move_to (2, 1),
                            [0, 2, 1, 3, 4])
        self._do_test_move (lambda store: store.move_to (2, 2),
                            None)
        self._do_test_move (lambda store: store.move_to (2, 3),
                            [0, 1, 3, 2, 4])
        self._do_test_move (lambda store: store.move_to (2, 4),
                            [0, 1, 3, 4, 2])


    def test_move_after (self):
        self._do_test_move (lambda store: store.move_after (2, 0),
                            [0, 2, 1, 3, 4])
        self._do_test_move (lambda store: store.move_after (2, 1),
                            None)
        self._do_test_move (lambda store: store.move_after (2, 2),
                            IndexError)
        self._do_test_move (lambda store: store.move_after (2, 3),
                            [0, 1, 3, 2, 4])
        self._do_test_move (lambda store: store.move_after (2, 4),
                            [0, 1, 3, 4, 2])


    def test_move_before (self):
        self._do_test_move (lambda store: store.move_before (2, 0),
                            [2, 0, 1, 3, 4])
        self._do_test_move (lambda store: store.move_before (2, 1),
                            [0, 2, 1, 3, 4])
        self._do_test_move (lambda store: store.move_before (2, 2),
                            IndexError)
        self._do_test_move (lambda store: store.move_before (2, 3),
                            None)
        self._do_test_move (lambda store: store.move_before (2, 4),
                            [0, 1, 3, 2, 4])


    def test_note_changes (self):
        store, emissions = _create_foo_list_store ()

        self.assertEqual (store.note_changes (1), 1)
        self.assertEqual (emissions.pop_all (), [('changed', (1,), 1)])

        self.assertEqual (store.note_changes (1, 0, -1, -2), 2)
        self.assertEqual (emissions.pop_all (), [('changed', (0,), 0),
                                                 ('changed', (1,), 1)])


    def _do_test_move (self, mover, expected_result):
        store, emissions = _create_foo_list_store ([0, 1, 2, 3, 4])

        if expected_result is None:
            mover (store)
            self.assertEqual (store[:], [0, 1, 2, 3, 4])
            self.assertEqual (emissions.pop_all (), [])

        elif isinstance (expected_result, list):
            mover (store)
            self.assertEqual (store[:], expected_result)
            self.assertEqual (emissions.pop_all (), [('reordered', '?' or expected_result)])

        else:
            self.assertRaises (expected_result, lambda: mover (store))



def _create_foo_list_store (values = None):
    if values is None:
        values = [Foo (1), Foo (2, 'abc')]

    store     = RowObjectListStore ([(int, 'foo'),
                                     (str, 'bar')],
                                    values)
    emissions = PopAllList ()

    store.connect ('row-changed',
                   lambda model, path, iter:
                       emissions.append (('changed', path, model.get_row_index (iter))))
    store.connect ('row-deleted',
                   lambda model, path:
                       emissions.append (('deleted', path)))
    store.connect ('row-inserted',
                   lambda model, path, iter:
                       emissions.append (('inserted', path, model.get_row_index (iter))))

    def reordered (model, path, iter, new_order):
        if not path and iter is None:
            # 'new_order' is not readable in Python (it is gobject.GPointer)...
            emissions.append (('reordered', '?'))
        else:
            emissions.append (('reordered', path, iter, '?'))

    store.connect ('rows-reordered', reordered)

    return store, emissions



if __name__ == '__main__':
    unittest.main ()



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
