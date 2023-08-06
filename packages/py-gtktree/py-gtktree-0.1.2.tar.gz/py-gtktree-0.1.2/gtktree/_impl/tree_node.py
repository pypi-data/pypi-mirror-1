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


import glib


__all__ = ('TreeNode', 'DefaultTreeNode', 'LazyDefaultTreeNode')



class TreeNode (object):

    __slots__ = ()

    @property
    def row_object (self):
        return self


    @property
    def parent_node (self): raise NotImplemented

    # Default implementation does nothing: if you have other way of deriving parent node
    # for the property, you can do so without implementing this method.
    def _set_parent_node (self, parent_node):
        pass


    @property
    def next_node (self): raise NotImplemented

    # Default implementation does nothing: if you have other way of deriving next node for
    # the property, you can do so without implementing this method.
    def _set_next_node (self, next_node):
        pass


    @property
    def previous_node (self):
        parent = self.parent_node
        if parent is None:
            return None

        index = parent.get_child_node_index (self)
        if index > 0:
            return parent.get_child_node (index - 1)
        else:
            return None


    @property
    def has_child_nodes_currently (self):
        return self.first_child_node is not None

    @property
    def has_child_nodes (self):
        return self.has_child_nodes_currently

    @property
    def num_child_nodes (self):
        child        = self.first_child_node
        num_children = 0

        while child is not None:
            num_children += 1
            child         = child.next_node

        return num_children

    @property
    def first_child_node (self): raise NotImplemented

    # Default implementation does nothing: if you have other way of deriving parent node
    # for the property, you can do so without implementing this method.
    def _set_first_child_node (self, first_child_node):
        pass


    def get_child_node (self, index):
        child = self.first_child_node
        if child is None:
            raise IndexError

        while index > 0:
            child = child.next_node
            if child is None:
                raise IndexError

            index -= 1

        return child

    def get_child_node_index (self, child):
        candidate = self.first_child_node
        index     = 0

        while candidate is not child:
            if candidate is None:
                raise ValueError

            index     += 1
            candidate  = candidate.next_node

        return index


    def get_tree_model (self):
        node   = self
        parent = node.parent_node

        while parent is not None:
            node   = parent
            parent = node.parent_node

        return node._do_get_tree_model ()

    def _do_get_tree_model (self):
        return None


    def compute_path (self):
        parent = self.parent_node
        if parent is None:
            return None

        row    = self
        index  = parent.get_child_node_index (row)
        row    = parent
        parent = row.parent_node

        if parent is None:
            return (index,)

        path   = [index]

        while parent is not None:
            path.append (parent.get_child_node_index (row))
            row    = parent
            parent = row.parent_node

        path.reverse ()
        return tuple (path)


    def delete_child_node (self, child):
        raise NotImplemented

    def insert_child_node (self, child, before = None):
        raise NotImplemented


    def hierarchic_copy (self):
        copy = type (self) ()
        if self.row_object is not self:
            copy.row_object = self.row_object

        child = self.first_child_node
        while child is not None:
            copy.insert_child_node (child.hierarchic_copy ())
            child = child.next_node

        return copy


    def __repr__(self):
        return '<%s.%s at 0x%x: %r>' % (type (self).__module__, type (self).__name__, id (self), self.row_object)



class DefaultTreeNode (TreeNode):

    __slots__ = ('_row_object', '__parent_node', '__next_node', '__child_nodes')


    def __init__(self, row_object = None, child_nodes = None):
        self.__parent_node = None
        self.__next_node   = None
        self.__child_nodes = None
        self.row_object    = row_object

        if child_nodes:
            self.child_nodes = child_nodes


    def _get_row_object (self):
        return self._row_object

    def _set_row_object (self, row_object):
        self._row_object = row_object

    row_object = property (_get_row_object, _set_row_object)
    del _get_row_object, _set_row_object


    @property
    def parent_node (self):
        return self.__parent_node

    def _set_parent_node (self, parent_node):
        self.__parent_node = parent_node


    def _get_child_nodes (self):
        child_nodes = self.__child_nodes

        if child_nodes is None:
            child_nodes = _DefaultTreeNodeChildren (self)
            self.__child_nodes = child_nodes

        return self.__child_nodes

    def _set_child_nodes (self, child_nodes):
        self.child_nodes[:] = child_nodes

    child_nodes = property (_get_child_nodes, _set_child_nodes)
    del _get_child_nodes, _set_child_nodes


    @property
    def next_node (self):
        return self.__next_node

    def _set_next_node (self, next_node):
        self.__next_node = next_node


    @property
    def has_child_nodes_currently (self):
        return bool (self.__child_nodes)

    @property
    def num_child_nodes (self):
        child_nodes = self.__child_nodes
        return len (child_nodes) if child_nodes is not None else 0

    @property
    def first_child_node (self):
        child_nodes = self.__child_nodes
        return child_nodes[0] if child_nodes else None

    def get_child_node (self, index):
        child_nodes = self.__child_nodes
        if child_nodes is not None and index >= 0:
            return child_nodes[index]
        else:
            return None

    def get_child_node_index (self, child):
        child_nodes = self.__child_nodes
        if child_nodes is not None:
            for index, candidate in enumerate (child_nodes):
                if candidate is child:
                    return index

        raise ValueError


    def delete_child_node (self, child):
        self.child_nodes.remove (child)

    def insert_child_node (self, child, before = None):
        if before is None:
            self.child_nodes.append (child)
        else:
            self.child_nodes.insert (self.child_nodes.index (before), child)



class _DefaultTreeNodeChildren (list):

    __slots__ = ('__node')

    def __init__(self, node):
        self.__node = node


    def append (self, child):
        model, path = self._get_tree_model_and_node_path ()
        self._do_insert (model, path, len (self), (child,))

    def insert (self, index, child):
        model, path = self._get_tree_model_and_node_path ()
        self._do_insert (model, path, index, (child,))

    def remove (self, value):
        del self[self.index (value)]


    # 'indices' *must* be between 0 and len (self) and *must* be in reverse order (largest
    # to smallest).  This is a low level function and so it doesn't verify anything.
    # Return number of removed rows (will be less than size of 'indices' if there are
    # duplicates).
    def _do_remove_at (self, model, path, indices):
        if not indices:
            return 0

        last_index  = None
        num_removed = 0

        for index in indices:
            if index == last_index:
                continue

            child = self[index]
            list.__delitem__(self, index)

            if index > 0:
                self[index - 1]._set_next_node (child.next_node)
            else:
                self.__node._set_first_child_node (child.next_node)

            child._set_parent_node (None)
            child._set_next_node (None)

            if model is not None:
                model.row_deleted (path + (index,))
                if not self and path:
                    model.row_has_child_toggled (path, model._do_get_iter (self.__node))

            last_index = index
            num_removed += 1

        return num_removed

    def _do_insert (self, model, path, index, nodes, after = False):
        current_child = (self[index] if index < len (self) else None)

        for child in nodes:
            list.insert (self, index, child)

            if index > 0:
                self[index - 1]._set_next_node (child)
            else:
                self.__node._set_first_child_node (child)

            child._set_parent_node (self.__node)
            child._set_next_node (current_child)

            if model is not None:
                child_path = path + (index,)
                child_iter = model._do_get_iter (child)
                model.row_inserted (child_path, child_iter)

                if len (self) == 1 and path:
                    model.row_has_child_toggled (path, model._do_get_iter (self.__node))

                if child.has_child_nodes_currently:
                    model.row_has_child_toggled (child_path, child_iter)

            index += 1

    def _get_tree_model_and_node_path (self):
        model = self.__node.get_tree_model ()
        if model is None:
            return None, None
        elif self.__node is not model.root:
            return model, model.get_path (model._do_get_iter (self.__node))
        else:
            return model, ()


    def __delitem__(self, index):
        model, path = self._get_tree_model_and_node_path ()

        if not isinstance (index, slice):
            self._do_remove_at (model, path, (index,))
        else:
            indices = range (index.start, min (index.stop, len (self)), index.step or 1)
            indices.reverse ()
            self._do_remove_at (model, path, indices)

    def __setitem__(self, index, node):
        model, path = self._get_tree_model_and_node_path ()

        if not isinstance (index, slice):
            self._do_remove_at (model, path, (index,))
            self._do_insert    (model, path, index, (node,))
            return

        new_children      = tuple (node)
        start, stop, step = index.indices (len (self))

        if step == 1:
            self._do_remove_at (model, path, range (stop - 1, start - 1, -1))
            self._do_insert    (model, path, start, new_children)
        else:
            indices = range (start, stop, step)
            if len (new_children) == len (indices):
                for index, child in zip (indices, new_children):
                    self._do_remove_at (model, path, (index,))
                    self._do_insert    (model, path, index, child)
            else:
                raise ValueError (('attempt to assign sequence of size %d '
                                   'to extended slice of size %d')
                                  % (len (new_children), len (indices)))


    if '__getslice__' in dir (list):
        def __getslice__(self, start, stop):
            self.__getitem__(slice (start, stop))

    if '__setslice__' in dir (list):
        def __setslice__(self, start, stop, sequence):
            self.__setitem__(slice (start, stop), sequence)

    if '__delslice__' in dir (list):
        def __delslice__(self, start, stop):
            self.__delitem__(slice (start, stop))



class LazyDefaultTreeNode (DefaultTreeNode):

    # 0 --- need loading;
    # 1 --- determined that there's at least one child, but didn't load;
    # 2 --- loading complete.
    __slots__ = ('__load_state')


    def __init__(self, row_object = None, child_nodes = None):
        super (LazyDefaultTreeNode, self).__init__(row_object, child_nodes)
        self.__load_state = (0 if not child_nodes else 2)


    # Default implementation actually just calls lazy_load().
    def lazy_has_children (self):
        self._do_lazy_load ()
        return self.has_child_nodes

    def lazy_load (self):
        raise NotImplemented


    def _determine_if_has_children (self):
        self.__load_state = 1
        if self.lazy_has_children ():
            child_nodes = super (LazyDefaultTreeNode, self).child_nodes
            if child_nodes:
                self.__load_state = 2
            else:
                child_nodes.append (DefaultTreeNode (_Placeholder ()))
        else:
            self.__load_state = 2

    def _do_lazy_load (self):
        self.__load_state = 2
        child_nodes       = self.child_nodes
        loaded_nodes      = tuple (self.lazy_load ())

        if not child_nodes or loaded_nodes:
            child_nodes[:] = loaded_nodes
        else:
            # We need to remove the fake placeholder node, but cannot do that now, because
            # that'll fuck tree view (for instance) up: first node claims to have
            # children, but then suddenly there are none...
            placeholder = child_nodes[0]

            def remove_placeholder_nodes ():
                try:
                    child_nodes.remove (placeholder)
                except ValueError:
                    # Maybe removed already...
                    pass

            glib.idle_add (remove_placeholder_nodes, priority = glib.PRIORITY_HIGH)


    def _get_child_nodes (self):
        child_nodes = super (LazyDefaultTreeNode, self).child_nodes
        if self.__load_state != 2:
            self._do_lazy_load ()

        return child_nodes

    child_nodes = property (_get_child_nodes, DefaultTreeNode.child_nodes.fset)
    del _get_child_nodes


    @property
    def has_child_nodes (self):
        if self.__load_state == 0:
            self._determine_if_has_children ()
        return super (LazyDefaultTreeNode, self).has_child_nodes

    @property
    def num_child_nodes (self):
        if self.__load_state != 2:
            self._do_lazy_load ()
        return super (LazyDefaultTreeNode, self).num_child_nodes

    @property
    def first_child_node (self):
        if self.__load_state != 2:
            self._do_lazy_load ()
        return super (LazyDefaultTreeNode, self).first_child_node

    def get_child_node (self, index):
        if self.__load_state != 2:
            self._do_lazy_load ()
        return super (LazyDefaultTreeNode, self).get_child_node (index)

    def get_child_node_index (self, child):
        if self.__load_state != 2:
            self._do_lazy_load ()
        return super (LazyDefaultTreeNode, self).get_child_node_index (child)



# FIXME: I'm not sure this is good enough, but it seems we manage to remove placeholders
#        before they are even queried for values.
class _Placeholder (object):

    def __getattr__(self, name):
        return None



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
