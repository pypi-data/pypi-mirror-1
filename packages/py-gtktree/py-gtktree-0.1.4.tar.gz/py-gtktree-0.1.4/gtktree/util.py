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


import gtk

from gtktree.model import RowObjectTreeModel


__all__ = ('TreeViewUtils',)



class TreeViewUtils (object):

    @staticmethod
    def get_selected_row (tree_view):
        model, iter = _do_get_selection (tree_view, False)
        if iter is not None:
            return model, model.get_row_object (iter)
        else:
            return None, None

    @staticmethod
    def get_selected_node (tree_view):
        model, iter = _do_get_selection (tree_view, False)
        if iter is not None:
            return model.get_node (iter)
        else:
            return None

    @staticmethod
    def get_selected_row_list (tree_view):
        model, paths = _do_get_selection (tree_view, False)
        return [(path, model.get_row_object (model.get_iter (path))) for path in paths]

    @staticmethod
    def get_selected_node_list (tree_view):
        model, paths = _do_get_selection (tree_view, False)
        return [model.get_node (model.get_iter (path)) for path in paths]


    @staticmethod
    def enable_standard_drags (tree_view):
        _check_tree_view (tree_view)

        start_button_mask = gtk.gdk.BUTTON1_MASK
        targets           = [('GTK_TREE_MODEL_ROW', gtk.TARGET_SAME_APP, 0)]
        action            = gtk.gdk.ACTION_MOVE

        tree_view.enable_model_drag_source (start_button_mask, targets, action)
        tree_view.enable_model_drag_dest (targets, action)


    @staticmethod
    def enable_renderer_editing (renderer, model, attribute):
        _check_tree_model (model)

        if 'editable' in renderer.props.__members__:
            renderer.props.editable = True

            def editing_started (renderer, editable, path):
                def editing_done (editable):
                    if isinstance (editable, gtk.Entry):
                        value = editable.props.text
                    elif isinstance (editable, gtk.SpinButton):
                        value = editable.props.value
                    elif isinstance (editable, gtk.ComboBoxEntry):
                        value = editable.child.props.text
                    # FIXME: elif isinstance (editable, gtk.ComboBox):
                    else:
                        raise TypeError ("unsupported gtk.Editable implementation %s.%s"
                                         % (editable.__module__, type (editable).__name__))

                    model.set_cell (model.get_iter (path), attribute, value)

                editable.connect ('editing-done', editing_done)

            renderer.connect ('editing-started', editing_started)

        elif 'activatable' in renderer.props.__members__:
            def toggled (renderer, path):
                iter = model.get_iter (path)
                model.set_cell (iter, attribute, not model.get_cell (iter, attribute))

            renderer.connect ('toggled', toggled)

        else:
            raise TypeError ("unsupported gtk.CellRenderer implementation %s.%s"
                             % (renderer.__module__, type (renderer).__name__))


    @staticmethod
    def connect_viewport_handler (tree_view, handler, *args):
        _check_tree_view (tree_view)
        return _ViewportHandler (tree_view, handler, args)

    @staticmethod
    def disconnect_viewport_handler (tree_view, composite_handler_id):
        _check_tree_view (tree_view)
        if not isinstance (composite_handler_id, _ViewportHandler):
            raise TypeError ("'composite_handler_id' must be the result of "
                             "a call to connect_viewport_handler()")

        composite_handler_id._disconnect (tree_view)


    @staticmethod
    def get_viewport_rows (tree_view):
        _check_tree_view (tree_view)
        if not tree_view.flags () & gtk.REALIZED:
            return []

        model = _get_row_object_model (tree_view)
        first = model.get_iter_first ()
        if first is None:
            return []

        from_path, to_path = tree_view.get_visible_range ()

        if model.get_flags () & gtk.TREE_MODEL_LIST_ONLY:
            from_index  = (from_path[0] if from_path is not None else 0)
            to_index    = (to_path[0]   if to_path   is not None else model.iter_n_children (None))
            iter        = model.iter_nth_child (None, from_index)
            row_objects = []

            for index in range (from_index, to_index + 1):
                row_objects.append ((iter, model.get_row_object (iter)))
                iter = model.iter_next (iter)

            return row_objects

        else:
            raise TypeError ("get_viewport_rows() currently cannot handle non-list models")



def _do_get_selection (tree_view, multiple):
    _check_tree_view (tree_view)

    selection = tree_view.get_selection ()
    if not multiple:
        result = selection.get_selected ()
    else:
        result = selection.get_selected_rows ()

    _check_tree_model (result[0])
    return result


def _check_tree_view (tree_view):
    if not isinstance (tree_view, gtk.TreeView):
        raise TypeError ("'tree_view' must be an instance of gtk.TreeView")

def _check_tree_model (model):
    if not isinstance (model, RowObjectTreeModel):
        raise TypeError ("'tree_view's model must be an instance of RowObjectTreeModel")

def _get_row_object_model (tree_view):
    model = tree_view.props.model
    if isinstance (model, RowObjectTreeModel):
        return model
    else:
        raise TypeError ("'tree_view's model must be an instance of RowObjectTreeModel")


class _ViewportHandler (object):

    def __init__(self, tree_view, handler, args):
        self._tree_view = tree_view
        self._handler   = handler
        self._args      = args

        self._h_notify_id        = tree_view.connect ('notify::hadjustment', self._reconnect)
        self._h_changed_id       = None
        self._h_value_changed_id = None
        self._v_notify_id        = tree_view.connect ('notify::vadjustment', self._reconnect)
        self._v_changed_id       = None
        self._v_value_changed_id = None

        self._reconnect ()


    def _reconnect (self):
        # Just a little precaution against illegal usage.
        if self._handler is None:
            raise RuntimeError

        hadjustment = self._tree_view.props.hadjustment
        vadjustment = self._tree_view.props.vadjustment

        if self._h_changed_id is None or not hadjustment.handler_is_connect (self._h_changed_id):
            if self._h_changed_id is not None:
                hadjustment.disconnect (self._h_changed_id)

            self._h_changed_id = hadjustment.connect ('changed', self._invoke_handler)

        if (self._h_value_changed_id is None
            or not hadjustment.handler_is_connect (self._h_value_changed_id)):
            if self._h_value_changed_id is not None:
                hadjustment.disconnect (self._h_value_changed_id)

            self._h_value_changed_id = hadjustment.connect ('value-changed', self._invoke_handler)

        if self._v_changed_id is None or not vadjustment.handler_is_connect (self._v_changed_id):
            if self._v_changed_id is not None:
                vadjustment.disconnect (self._v_changed_id)

            self._v_changed_id = vadjustment.connect ('changed', self._invoke_handler)

        if (self._v_value_changed_id is None
            or not vadjustment.handler_is_connect (self._v_value_changed_id)):
            if self._v_value_changed_id is not None:
                vadjustment.disconnect (self._v_value_changed_id)

            self._v_value_changed_id = vadjustment.connect ('value-changed', self._invoke_handler)


    def _invoke_handler (self, adjustment):
        self._handler (self._tree_view, *self._args)


    def _disconnect (self, tree_view):
        if tree_view != self._tree_view:
            raise RuntimeError ("handler is not connected to the tree view")

        hadjustment = tree_view.props.hadjustment
        vadjustment = tree_view.props.vadjustment

        hadjustment.disconnect (self._h_notify_id)
        hadjustment.disconnect (self._h_changed_id)
        hadjustment.disconnect (self._h_value_changed_id)

        vadjustment.disconnect (self._v_notify_id)
        vadjustment.disconnect (self._v_changed_id)
        vadjustment.disconnect (self._v_value_changed_id)

        self._tree_view = None
        self._handler   = None
        self._args      = None



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
