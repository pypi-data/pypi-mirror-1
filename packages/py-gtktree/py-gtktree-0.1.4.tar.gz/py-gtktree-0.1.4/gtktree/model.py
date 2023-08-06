# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------#
# This file is part of Py-gtktree.                                         #
#                                                                          #
# Copyright (C) 2006, 2007, 2008, 2009 Paul Pogonyshev.                    #
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


import gtk
import operator

from bisect import bisect_right


__all__ = ('RowObjectTreeModel',
           'RowObjectListStore',
           'TreeNode', 'DefaultTreeNode', 'LazyDefaultTreeNode', 'RowObjectTreeStore')


# Should be available on 2.6 and up.
_HAVE_DOTTED_ATTRGETTER_SUPPORT = False

try:
    if operator.attrgetter ('attrgetter.__call__') (operator) == operator.attrgetter.__call__:
        _HAVE_DOTTED_ATTRGETTER_SUPPORT = True
except:
    pass



class _Columns (tuple):

    def __call__(self, attribute):
        for k, entry in enumerate (self):
            if entry[1] == attribute:
                return k

        raise ValueError ("there is no column for attribute '%s'" % attribute)



class RowObjectTreeModel (gtk.GenericTreeModel):

    def __init__(self, columns):
        self.__getters = []
        self.__setters = []
        self.__columns = _Columns (columns)

        for g_type, attribute in self.__columns:
            if isinstance (attribute, basestring):
                getter = _attrgetter (attribute)
                setter = _attrsetter (attribute)
            else:
                assert callable (attribute)
                getter = attribute
                setter = _raising_attrsetter

            self.__getters.append (getter)
            self.__setters.append (setter)

        gtk.GenericTreeModel.__init__(self)

        self.__object_type          = None
        self.__foreign_drags_policy = None
        self.__default_node_type    = DefaultTreeNode


    @property
    def columns (self):
        return self.__columns

    def _get_column_getter (self, index):
        return self.__getters[index]


    @property
    def node_based (self):
        return False


    @property
    def root (self):
        if self.node_based:
            raise NotImplementedError
        else:
            raise TypeError ("only node-based models can have a root node")


    # Strictly speaking, this property only makes sense for node-based model.

    def _get_default_node_type (self):
        return self.__default_node_type

    def _set_default_node_type (self, default_node_type):
        if not issubclass (default_node_type, TreeNode):
            raise TypeError ("'default_node_type' must be a subtype of TreeNode")

        self.__default_node_type = default_node_type

    default_node_type = property (_get_default_node_type, _set_default_node_type)
    del _get_default_node_type, _set_default_node_type


    def get_cell (self, row, attribute):
        return self.get_value (self._do_get_iter (row), self.columns (attribute))

    def set_cell (self, row, attribute, value):
        iter = self._do_get_iter (row)
        self.__setters[self.columns (attribute)] (self.get_row_object (iter), value)
        self.note_changes (iter)


    def on_get_n_columns (self):
        return len (self.__columns)

    def on_get_column_type (self, index):
        return self.__columns[index][0]


    def on_get_value (self, row, column):
        return self.__getters[column] (self._do_get_row_object (row))

    def get_row_object (self, iter):
        return self._do_get_row_object (self.get_user_data (iter))

    def get_node (self, iter):
        return self._do_get_node (self.get_user_data (iter))

    def _do_get_row_object (self, row):
        raise NotImplementedError

    def _do_get_node (self, row):
        if self.node_based:
            raise NotImplementedError
        else:
            raise RuntimeError ("this model is not node-based")

    def _do_get_iter (self, row):
        raise NotImplementedError


    @property
    def is_sorted (self):
        return False

    def _check_is_not_sorted (self):
        if self.is_sorted:
            raise RuntimeError ("the model must not be user-sorted")


    def note_changes (self, *rows):
        if not rows:
            return 0

        row_data = []
        for row in rows:
            iter = self._do_get_iter (row)
            row_data.append ((self.get_path (iter), iter))

        row_data.sort (key = operator.itemgetter (0))

        last_path   = None
        num_changed = 0

        for path, iter in row_data:
            if path == last_path:
                continue

            self.row_changed (path, iter)

            last_path    = path
            num_changed += 1

        return num_changed


    def _compute_child_node_insertion_point (self, child_nodes, new_child):
        if self.node_based:
            raise NotImplementedError
        else:
            raise TypeError ("can only be called on node-based models")

    def _do_apply_sort_settings_to_node (self, node):
        if self.node_based:
            raise NotImplementedError
        else:
            raise TypeError ("can only be called on node-based models")


    def _get_object_type (self):
        return self.__object_type

    def _set_object_type (self, object_type):
        self.__object_type = object_type

    object_type = property (_get_object_type, _set_object_type)
    del _get_object_type, _set_object_type


    def is_accepting_drags_from (self, source_model):
        if source_model is self:
            return True

        foreign_drags_policy = self.foreign_drags_policy

        if foreign_drags_policy is None:
            if self.object_type is None:
                return False
            else:
                return source_model.object_type == self.object_type
        elif isinstance (foreign_drags_policy, bool):
            return foreign_drags_policy
        else:
            return foreign_drags_policy (self, source_model)


    def _get_foreign_drags_policy (self):
        return self.__foreign_drags_policy

    def _set_foreign_drags_policy (self, foreign_drags_policy):
        if not (foreign_drags_policy is None
                or isinstance (foreign_drags_policy, bool)
                or callable (foreign_drags_policy)):
            raise TypeError ("'foreign_drags_policy' must be None, True, Flase or a callable")

        self.__foreign_drags_policy = foreign_drags_policy

    foreign_drags_policy = property (_get_foreign_drags_policy, _set_foreign_drags_policy)
    del _get_foreign_drags_policy, _set_foreign_drags_policy


    def _get_drag_data (self, selection_data):
        source_model, source_path = selection_data.tree_get_row_drag_data ()
        if not self.is_accepting_drags_from (source_model):
            return None, None, None

        source_iter = source_model.get_iter (source_path)

        if not self.node_based:
            element = source_model.get_row_object (source_iter)
        elif source_model.node_based:
            element = source_model.get_node (source_iter)
        else:
            row = source_model.get_row_object (source_iter)

            if isinstance (row, TreeNode) and row.row_object is row:
                element = row
            else:
                element            = self.default_node_type ()
                element.row_object = row

        return source_model, source_path, element



if not hasattr (gtk, 'TREE_SORTABLE_DEFAULT_SORT_COLUMN_ID'):
    from gtktree._impl import c_hacks

    _USING_C_HACKS = True
    _UNSORTED      = c_hacks.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID
    _DEFAULT_SORT  = c_hacks.TREE_SORTABLE_DEFAULT_SORT_COLUMN_ID

else:
    _USING_C_HACKS = False
    _UNSORTED      = gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID
    _DEFAULT_SORT  = gtk.TREE_SORTABLE_DEFAULT_SORT_COLUMN_ID



# A (currently internal) mixin that helps with implementing gtk.TreeSortable interface.
# Note that it _must_ be listed before anything inheriting gtk.TreeModel for correct MRO.
# Relies on inherited class to have 'columns' property and _do_apply_sort_settings()
# method.
class _TreeSortableHelper (object):

    def __init__(self):
        self._sort_column_id = _UNSORTED
        self._sort_ascending = True

        if self._support_classic_sort_functions:
            self.__default_sort_function = None
            self.__sort_functions        = []


    @property
    def is_sorted (self):
        return self._sort_column_id != _UNSORTED

    @property
    def _support_classic_sort_functions (self):
        return True


    def _get_current_sort_function (self):
        if self._sort_column_id != _UNSORTED and self._support_classic_sort_functions:
            if self._sort_column_id == _DEFAULT_SORT:
                return self.__default_sort_function
            elif self._sort_column_id < len (self.__sort_functions):
                return self.__sort_functions[self._sort_column_id]

        return None        


    def do_get_sort_column_id (self):
        return (self._sort_column_id,
                gtk.SORT_ASCENDING if self._sort_ascending else gtk.SORT_DESCENDING)


    def do_set_sort_column_id (self, sort_column_id, sort_ascending):
        sort_ascending = (sort_ascending == gtk.SORT_ASCENDING)
        if self._sort_column_id == sort_column_id and self._sort_ascending == sort_ascending:
            return

        self._sort_column_id = sort_column_id
        self._sort_ascending = sort_ascending

        self.sort_column_changed ()

        if sort_column_id != _UNSORTED:
            self._do_apply_sort_settings ()


    def do_set_sort_func (self, sort_column_id, func):
        if not self._support_classic_sort_functions:
            raise RuntimeError ("sort functions are not supported in this model")

        if 0 <= sort_column_id and sort_column_id < len (self.columns):
            if len (self.__sort_functions) <= sort_column_id:
                self.__sort_functions.extend ([None] * (1 + sort_column_id
                                                        - len (self.__sort_functions)))

            self.__sort_functions[sort_column_id] = func
            if self._sort_column_id == sort_column_id:
                self._do_apply_sort_settings ()

        else:
            raise IndexError


    def do_has_default_sort_func (self):
        return self._support_classic_sort_functions and self.__default_sort_function is not None

    def do_set_default_sort_func (self, func):
        if not self._support_classic_sort_functions:
            raise RuntimeError ("sort functions are not supported in this model")

        self.__default_sort_function = func
        if self._sort_column_id == _DEFAULT_SORT:
            self._do_apply_sort_settings ()



# IMPLEMENTATION NOTES
#
# Iterator user data are indices of the rows (i.e., 0, ..., N-1 where N is list length).
# Index instances are kept in list '_indices': we must _always_ use these for creating
# iterators, otherwise there can be refcount corruption.  Because we have own persistent
# references to iterator user data, we can set 'leak_references' to False.  Note that
# iterators don't survive list store modifications except for appending to the end.

class RowObjectListStore (_TreeSortableHelper, RowObjectTreeModel,
                          gtk.TreeSortable, gtk.TreeDragSource, gtk.TreeDragDest):

    __gtype_name__ = 'RowObjectListStore'

    def __init__(self, columns, values = None):
        if values is None:
            self._values  = []
            self._indices = []
        else:
            self._values  = list (values)
            self._indices = range (len (self._values))

        RowObjectTreeModel.__init__(self, columns)
        _TreeSortableHelper.__init__(self)

        self.props.leak_references = False


    def get_row_index (self, iter_or_path):
        if not isinstance (iter_or_path, gtk.TreeIter):
            iter_or_path = self.get_iter (iter_or_path)
        return self.get_user_data (iter_or_path)


    def index (self, row_object, i = None, j = None):
        values = self._values
        i      = (0            if i is None else self._get_insertion_point (i))
        j      = (len (values) if j is None else self._get_insertion_point (j))

        return values.index (row_object, i, j)

    def count (self, row_object):
        return self._values.count (row_object)


    def append (self, *row_objects):
        return self._do_insert (len (self._values), row_objects)

    def prepend (self, *row_objects):
        return self._do_insert (0, row_objects)

    def insert (self, index, *row_objects):
        return self._do_insert (index, row_objects)

    def insert_before (self, index, *row_objects):
        return self._do_insert (index, row_objects)

    def insert_after (self, index, *row_objects):
        return self._do_insert (index, row_objects, True)

    def extend (self, row_objects):
        self._do_insert (len (self._values), row_objects)


    def _do_insert (self, index, row_objects, after = False):
        if not row_objects:
            return

        if self.is_sorted:
            return self._do_insert_sorted (row_objects)

        values  = self._values
        indices = self._indices

        # Special case: insertion allows None as 'index' to simplify using iter_next()
        # which can return None as insertion point.
        if index is None:
            index = (0 if after else len (values))
        else:
            index = self._get_insertion_point (index, after)

        if index < len (values):
            self.invalidate_iters ()

        if len (row_objects) == 1:
            indices.append (len (indices))
            values.insert (index, row_objects[0])

            iter = self.get_iter (index)
            self.row_inserted (index, iter)

            return iter

        else:
            indices.extend (range (len (indices), len (indices) + len (row_objects)))
            for row_object in row_objects:
                values.insert (index, row_object)
                self.row_inserted (index, self.get_iter (index))
                index += 1


    def _do_insert_sorted (self, row_objects):
        compare = self._get_current_sort_function ()

        values         = self._values
        indices        = self._indices
        sort_ascending = self._sort_ascending

        self.invalidate_iters ()
        indices.extend (range (len (indices), len (indices) + len (row_objects)))

        # FIXME: Really need to think it out.  Currently, this is quite ugly.
        if compare is not None:
            for row_object in row_objects:
                values.append (row_object)
                index = self.__bisect_with_classic_sort_function (compare)

                if index < len (values) - 1:
                    del values[-1]
                    values.insert (index, row_object)

                last_iter = self.get_iter (index)
                self.row_inserted (index, last_iter)

        else:
            # FIXME: Suboptimal for larger lists: we don't really need to get all values.
            #        Make this lazy.
            getter      = self._get_column_getter (self._sort_column_id)
            sort_values = [getter (value) for value in values]

            if not sort_ascending:
                sort_values.reverse ()

            for row_object in row_objects:
                value = getter (row_object)
                index = bisect_right (sort_values, value)

                sort_values.insert (index, value)

                if not sort_ascending:
                    index = len (values) - index

                values.insert (index, row_object)

                last_iter = self.get_iter (index)
                self.row_inserted (index, last_iter)

        if len (row_objects) == 1:
            return last_iter


    # Currently assumes that the new row object is at the last position.
    def __bisect_with_classic_sort_function (self, compare):
        if len (self) == 1:
            return 0

        from_    = 0
        to_      = len (self) - 1
        new_iter = self.create_tree_iter (to_)

        while from_ < to_:
            compare_to = (from_ + to_) / 2
            result     = compare (self, new_iter, self.create_tree_iter (compare_to))

            if result > 0:
                from_ = compare_to + 1
            elif result < 0:
                to_ = compare_to
            else:
                return compare_to

        return from_


    def remove (self, row_object):
        del self[self._values.index (row_object)]

    def remove_at (self, *indices):
        if not indices:
            return

        indices = list (indices)
        for k, index in enumerate (indices):
            indices[k] = self._get_existing_row_index (index)

        indices.sort (reverse = True)
        return self._do_remove_at (indices)

    # 'indices' *must* be a non-empty list of integers between 0 and len(self) and it
    # *must* hold that indices[k] >= indices[k+1].  This is a low level function and so it
    # doesn't verify anything.  Return number of removed rows (will be less than size of
    # 'indices' if there are duplicates).
    def _do_remove_at (self, indices):
        last_index  = None
        num_removed = 0

        self.invalidate_iters ()

        for index in indices:
            if index == last_index:
                continue

            del self._values[index]
            self.row_deleted (index)

            last_index = index
            num_removed += 1

        del self._indices[-num_removed:]
        return num_removed


    def pop (self, index = -1):
        index = self._get_existing_row_index (index)
        row_object = self._values[index]
        del self[index]

        return row_object


    def clear (self):
        if self._values:
            del self[:]


    def reorder (self, new_order):
        self._check_is_not_sorted ()

        # Since we will (possibly) modify the list below, we make a copy.  Also, this
        # allows to accept any iterable argument.
        new_order = list (new_order)
        values    = self._values
        if len (new_order) != len (values):
            raise ValueError

        is_copied  = [False] * len (values)
        new_values = [None]  * len (values)

        for to_, from_ in enumerate (new_order):
            from_          = self._get_existing_row_index (from_)
            new_order[to_] = from_

            if not is_copied[from_]:
                new_values[to_]  = values[from_]
                is_copied[from_] = True
            else:
                raise ValueError

        self.invalidate_iters ()
        self._values = new_values

        self.rows_reordered ((), None, new_order)


    def reverse (self):
        self._check_is_not_sorted ()
        if not self._values:
            return

        new_order = range (len (self._values))
        new_order.reverse ()

        self.invalidate_iters ()
        self._values.reverse ()

        self.rows_reordered ((), None, new_order)


    def sort (self, cmp = None, key = None, reverse = False):
        self._check_is_not_sorted ()
        if len (self) <= 1:
            return

        values = zip (self._values, range (len (self)))
        values.sort (cmp     = (None if cmp is None else (lambda a, b: cmp (a[0], b[0]))),
                     key     = (None if key is None else (lambda a: key (a[0]))),
                     reverse = reverse)

        self._handle_new_value_order (values)


    def swap (self, index1, index2):
        self._check_is_not_sorted ()

        index1 = self._get_existing_row_index (index1)
        index2 = self._get_existing_row_index (index2)

        if index1 == index2:
            return

        values = self._values
        values[index1], values[index2] = values[index2], values[index1]

        # See http://bugzilla.gnome.org/show_bug.cgi?id=156244.  We are _required_ to emit
        # 'rows-reordered' signal here, not two 'row-changed'.
        new_order = range (len (values))
        new_order[index1], new_order[index2] = index2, index1

        self.rows_reordered ((), None, new_order)


    def move_to (self, from_index, to_index):
        self._check_is_not_sorted ()
        self._do_move (self._get_existing_row_index (from_index),
                       min (self._get_insertion_point (to_index), len (self._values) - 1))

    def move_before (self, from_index, before_index):
        self._check_is_not_sorted ()

        from_index   = self._get_existing_row_index (from_index)
        before_index = self._get_existing_row_index (before_index)

        if from_index > before_index:
            self._do_move (from_index, before_index)
        elif from_index < before_index:
            self._do_move (from_index, before_index - 1)
        else:
            raise IndexError ("'from_index' and 'before_index' specify the same row %d"
                              % from_index)

    def move_after (self, from_index, after_index):
        self._check_is_not_sorted ()

        from_index  = self._get_existing_row_index (from_index)
        after_index = self._get_existing_row_index (after_index)

        if from_index < after_index:
            self._do_move (from_index, after_index)
        elif from_index > after_index:
            self._do_move (from_index, after_index + 1)
        else:
            raise IndexError ("'from_index' and 'after_index' specify the same row %d"
                              % from_index)

    def _do_move (self, from_index, to_index):
        if from_index != to_index:
            new_order = range (len (self))
            self._values.insert (to_index, self._values.pop (from_index))
            new_order   .insert (to_index, new_order   .pop (from_index))

            self.rows_reordered ((), None, new_order)

    def _handle_new_value_order (self, reordered_values):
        self.invalidate_iters ()
        self._values = [value for value, index in reordered_values]

        new_order = [False] * len (self)
        for new_index, entry in enumerate (reordered_values):
            value, index         = entry
            new_order[new_index] = index

        self.rows_reordered ((), None, new_order)


    def note_changes (self, *rows):
        num_changed = super (RowObjectListStore, self).note_changes (*rows)

        # FIXME: Really non-optimal.  We don't need to resort all the model if a few
        #        (especially one) row has been changed.
        if self.is_sorted and num_changed > 0:
            self._do_apply_sort_settings ()

        return num_changed


    def __len__(self):
        return len (self._values)


    def __contains__(self, row_object):
        return row_object in self._values

    def __iter__(self):
        return iter (self._values)


    def __getitem__(self, index):
        if not isinstance (index, slice):
            return self._values[self._get_existing_row_index (index)]
        else:
            return self._values[index]

    def __setitem__(self, index, row_object):
        if not isinstance (index, slice):
            index = self._get_existing_row_index (index)
            self._values[index] = row_object
            self.row_changed (index, self.get_iter (index))

            # FIXME: Really non-optimal.  We don't need to resort all the model.
            if self.is_sorted:
                self._do_apply_sort_settings ()

            return

        row_objects       = tuple (row_object)
        start, stop, step = index.indices (len (self._values))

        if index.step is None:
            common_length = min (stop - start, len (row_objects))
            for k in range (common_length):
                _index = start + k
                self._values[_index] = row_objects[k]
                self.row_changed (_index, self.get_iter (_index))

            # FIXME: Really non-optimal.  We don't need to resort all the model if a few
            #        (especially one) row has been changed.
            if self.is_sorted:
                self._do_apply_sort_settings ()

            if len (row_objects) > common_length:
                self._do_insert (start + common_length, row_objects[common_length:])
            elif stop - start > common_length:
                self._do_remove_at (range (stop - 1, start + common_length - 1, -1))
        else:
            indices = range (start, stop, step)
            if len (row_objects) == len (indices):
                for index, row_object in zip (indices, row_objects):
                    self._values[index] = row_object
                    self.row_changed (index, self.get_iter (index))

                # FIXME: Really non-optimal.  We don't need to resort all the model if a
                #        few (especially one) row has been changed.
                if self.is_sorted:
                    self._do_apply_sort_settings ()
            else:
                raise ValueError (('attempt to assign sequence of size %d '
                                   'to extended slice of size %d')
                                  % (len (row_objects), len (indices)))

    def __delitem__(self, index):
        if not isinstance (index, slice):
            index = self._get_existing_row_index (index)

            del self._values[index]
            del self._indices[len (self._indices) - 1]

            self.invalidate_iters ()
            self.row_deleted (index)

        else:
            indices = range (*index.indices (len (self)))
            indices.reverse ()
            self._do_remove_at (indices)


    def _get_existing_row_index (self, index):
        if isinstance (index, gtk.TreeIter):
            return self.get_user_data (index)
        else:
            integer_index = operator.index (index)
            if integer_index < 0:
                integer_index += len (self)
                if integer_index >= 0:
                    return integer_index
            elif integer_index < len (self._values):
                return integer_index

        raise self._create_index_error (index)

    def _get_insertion_point (self, index, after = False):
        if isinstance (index, gtk.TreeIter):
            index = self.get_user_data (index)
            return index + 1 if after else index
        else:
            index = operator.index (index)
            size  = len (self._values)
            if index < 0:
                index += size
            if after:
                index += 1

            return max (0, min (index, size))

    def _create_index_error (self, index):
        return IndexError ("invalid row index %s: "
                           "only integers in range %d..%d (inclusive) and gtk.TreeIter are valid)"
                           % (index, -len (self), len (self) - 1))


    def on_get_flags (self):
        return gtk.TREE_MODEL_LIST_ONLY


    def _do_get_row_object (self, row):
        return self._values[row]

    def _do_get_iter (self, row):
        if isinstance (row, gtk.TreeIter):
            return row
        else:
            return self.create_tree_iter (self._get_existing_row_index (row))


    def on_get_iter (self, path):
        if self._values:
            return self._indices[path[0]]
        else:
            return None

    def on_get_path (self, row):
        return row


    def on_iter_parent (self, row):
        return None

    def on_iter_next (self, row):
        if row + 1 < len (self._values):
            return self._indices[row + 1]
        else:
            return None

    def on_iter_has_child (self, row):
        return False

    def on_iter_children (self, row):
        if row is None and self._values:
            return self._indices[0]
        else:
            return None

    def on_iter_n_children (self, row):
        if row is None:
            return len (self._values)
        else:
            return 0

    def on_iter_nth_child (self, parent, n):
        if parent is None:
            return self._indices[n]
        else:
            return None


    # Implementing gtk.TreeSortable.  Note that this relies on support from
    # _TreeSortableHelper and from our internal 'c_hacks' module if needed (on older
    # PyGTK).

    def _do_apply_sort_settings (self):
        values = zip (self._values, range (len (self)))

        compare = self._get_current_sort_function ()

        if compare is not None:
            values.sort (cmp     = lambda a, b: compare (self,
                                                         self.create_tree_iter (a[1]),
                                                         self.create_tree_iter (b[1])),
                         reverse = not self._sort_ascending)
        elif self._sort_column_id != _DEFAULT_SORT:
            getter = self._get_column_getter (self._sort_column_id)
            values.sort (key     = lambda a: getter (a[0]),
                         reverse = not self._sort_ascending)

        self._handle_new_value_order (values)


    # Implementing gtk.TreeDragSource.

    def do_row_draggable (self, path):
        return True

    def do_drag_data_delete (self, path):
        del self[path[0]]
        return True

    def do_drag_data_get (self, path, selection_data):
        return selection_data.tree_set_row_drag_data (self, path)


    # Implementing gtk.TreeDragDest.

    def do_drag_data_received (self, dest_path, selection_data):
        source_model, source_path, row_object = self._get_drag_data (selection_data)

        if source_model is not None:
            self.insert (dest_path[0], row_object)
            return True
        else:
            return False

    def do_row_drop_possible (self, dest_path, selection_data):
        if self.is_sorted:
            source_model, source_path, row_object = self._get_drag_data (selection_data)
            if source_model is self:
                return False

        return True


if _USING_C_HACKS:
    c_hacks.register_tree_sortable_implementation (RowObjectListStore)



from gtktree._impl.tree_node import TreeNode, DefaultTreeNode, LazyDefaultTreeNode

TreeNode           .__module__ = __name__
DefaultTreeNode    .__module__ = __name__
LazyDefaultTreeNode.__module__ = __name__


# IMPLEMENTATION NOTES
#
# Iterator user data are the nodes themselves.  Because of this, we can set
# 'leak_references' to False.  Also, by definition, iterators survive all tree store
# modifications.

class RowObjectTreeStore (_TreeSortableHelper, RowObjectTreeModel,
                          gtk.TreeSortable, gtk.TreeDragSource, gtk.TreeDragDest):

    __gtype_name__ = 'RowObjectTreeStore'

    def __init__(self, columns, top_level_nodes = None):
        # This postponed initialization allows to avoid unnecessary signal emissions.
        self.__root            = _RootTreeNode (None, top_level_nodes)
        self.__root.row_object = self

        RowObjectTreeModel.__init__(self, columns)
        _TreeSortableHelper.__init__(self)

        self.props.leak_references = False


    @property
    def node_based (self):
        return True


    @property
    def root (self):
        return self.__root


    def note_changes (self, *rows):
        num_changed = super (RowObjectTreeStore, self).note_changes (*rows)

        if self.is_sorted:
            unique_parents = set ()
            for row in rows:
                unique_parents.add (self.get_node (self._do_get_iter (row)).parent_node)

            self._do_apply_sort_settings (unique_parents)

        return num_changed


    def __len__(self):
        # Default value comes from gtk.GenericTreeModel.
        raise TypeError ("object of type '%s' has no len()" % type (self).__name__)

    def __contains__(self, row_object):
        for node in self.root.depth_first_order (False):
            if node.row_object == row_object:
                return True

        return False

    def __iter__(self):
        # Default value comes from gtk.GenericTreeModel.
        raise TypeError ("'%s' object is not iterable" % type (self).__name__)


    def on_get_flags (self):
        return gtk.TREE_MODEL_ITERS_PERSIST


    def _do_get_row_object (self, row):
        return row.row_object

    def _do_get_node (self, row):
        return row

    def _do_get_iter (self, row):
        if isinstance (row, gtk.TreeIter):
            return row
        else:
            return self.create_tree_iter (row)


    def on_get_iter (self, path):
        node = self.root
        for index in path:
            node = node.get_child_node (index)
        return node

    def on_get_path (self, row):
        return row.compute_path ()


    def on_iter_parent (self, row):
        parent = row.parent_node
        return parent if parent is not self.root else None

    def on_iter_next (self, row):
        return row.next_node

    def on_iter_has_child (self, row):
        return row.has_child_nodes

    def on_iter_children (self, row):
        return row.first_child_node

    def on_iter_n_children (self, row):
        return (row if row is not None else self.root).num_child_nodes

    def on_iter_nth_child (self, parent, n):
        if parent is not None:
            return parent.get_child_node (n)
        else:
            return self.root.get_child_node (n)


    def _compute_child_node_insertion_point (self, child_nodes, new_child):
        getter         = self._get_column_getter (self._sort_column_id)
        sort_values    = [getter (node.row_object) for node in child_nodes]
        sort_ascending = self._sort_ascending

        if not sort_ascending:
            sort_values.reverse ()

        index = bisect_right (sort_values, getter (new_child.row_object))
        return index if sort_ascending else len (child_nodes) - index


    # Implementing gtk.TreeSortable.  Note that this relies on support from
    # _TreeSortableHelper and from our internal 'c_hacks' module if needed (on older
    # PyGTK).

    # FIXME: Should support eventually.
    @property
    def _support_classic_sort_functions (self):
        return False

    def _do_apply_sort_settings_to_node (self, node):
        self._do_apply_sort_settings (tuple (child for child in node.depth_first_order ()
                                             if child.has_child_nodes_currently))

    def _do_apply_sort_settings (self, nodes = None):
        if self._sort_column_id != _DEFAULT_SORT:
            getter          = self._get_column_getter (self._sort_column_id)
            sort_descending = not self._sort_ascending

            if nodes is None:
                # Note: we are making a copy of the order since there will be structural
                # modifications.
                nodes = tuple (self.root.depth_first_order ())

            for node in nodes:
                num_child_nodes = node.num_child_nodes_currently
                if num_child_nodes < 2:
                    continue

                child_nodes = zip (node.build_child_node_list (), range (num_child_nodes))
                child_nodes.sort (key     = lambda a: getter (a[0].row_object),
                                  reverse = sort_descending)

                new_order = [False] * num_child_nodes
                for new_index, entry in enumerate (child_nodes):
                    value, index         = entry
                    new_order[new_index] = index

                node.reorder_child_nodes (new_order, True)


    # Implementing gtk.TreeDragSource.

    def do_row_draggable (self, path):
        node = self.get_node (self.get_iter (path))
        return node.is_draggable

    def do_drag_data_delete (self, path):
        node = self.get_node (self.get_iter (path))
        node.parent_node.delete_child_node (node)
        return True

    def do_drag_data_get (self, path, selection_data):
        return selection_data.tree_set_row_drag_data (self, path)


    # Implementing gtk.TreeDragDest.

    def do_drag_data_received (self, dest_path, selection_data):
        source_model, source_path, node = self._get_drag_data (selection_data)
        if source_model is None:
            return False

        dest_parent, dest_before = self._get_drag_destination_nodes (dest_path)
        dest_parent.insert_child_node (node.hierarchic_copy (), dest_before)
        return True

    def do_row_drop_possible (self, dest_path, selection_data):
        source_model, source_path, node = self._get_drag_data (selection_data)
        if source_model is None:
            return False

        dest_parent, dest_before = self._get_drag_destination_nodes (dest_path)
        if node is dest_parent or node.is_ancestor (dest_parent):
            return False

        if self.is_sorted and node.parent_node == dest_parent:
            return False

        return (dest_parent.accepts_dragged_child_node (node)
                and node.accepts_parent_node_after_drag (dest_parent))

    def _get_drag_destination_nodes (self, dest_path):
        if dest_path[-1] > 0:
            dest_path      = list (dest_path)
            dest_path[-1] -= 1

            dest_node = self.get_node (self.get_iter (tuple (dest_path)))
            return dest_node.parent_node, dest_node.next_node

        elif len (dest_path) > 1:
            dest_node_parent = self.get_node (self.get_iter (dest_path[:-1]))
            return dest_node_parent, dest_node_parent.first_child_node

        else:
            return self.root, self.root.first_child_node


if _USING_C_HACKS:
    c_hacks.register_tree_sortable_implementation (RowObjectTreeStore)



class _RootTreeNode (DefaultTreeNode):

    def _do_get_tree_model (self):
        return self.row_object

    def _set_row_object (self, row_object):
        if not hasattr (self, '_row_object') or self._row_object is None:
            self._row_object = row_object
        else:
            raise RuntimeError ("cannot change row object of a model's tree root node")

    row_object = property (DefaultTreeNode.row_object.fget, _set_row_object)
    del _set_row_object



def _attrgetter (attribute):
    if '.' not in attribute or _HAVE_DOTTED_ATTRGETTER_SUPPORT:
        return operator.attrgetter (attribute)
    else:
        name_parts = attribute.split ('.')
        def dotted_attrgetter (object):
            value = object
            for part in name_parts:
                value = getattr (value, part)
            return value

    return dotted_attrgetter


def _attrsetter (attribute):
    base, dot, final_attribute = attribute.rpartition ('.')

    if base:
        base_getter = _attrgetter (base)
        def composite_setter (object, value):
            setattr (base_getter (object), final_attribute, value)

        return composite_setter

    else:
        def simple_setter (object, value):
            setattr (object, final_attribute, value)

        return simple_setter


def _raising_attrsetter (attribute):
    raise TypeError ("this attribute cannot be modified")


# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
