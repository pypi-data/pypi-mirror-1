#! /usr/bin/env python
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

# Demonstrates how it is possible to edit a RowObjectTreeStore.  All basic editing
# operations plus drag'n'drop are possible.


#-- Importing and other auxiliary stuff ------------------------------

# If standalone, use Py-gtktree from the distribution, not installed.
if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))

try:
    from gtktree.model import RowObjectTreeStore, DefaultTreeNode
    from gtktree.util  import TreeViewUtils
except ImportError:
    sys.excepthook (*sys.exc_info ())
    sys.exit ("Please build Py-gtktree by executing 'python setup.py build' first")


import gtk
import os.path
import random
import sys


#-- EXAMPLE: Creating the tree model ---------------------------------

class Row (object):
    def __init__(self, name = None, description = None):
        self.name        = name
        self.description = description
        self.is_active   = False

store = RowObjectTreeStore ([(str,  'name'),
                             (str,  'description'),
                             (bool, 'is_active')])


#-- Loading UI definition --------------------------------------------

ui = gtk.Builder ()
ui.add_from_file (os.path.join (os.path.dirname (sys.argv[0]), 'editing_tree.ui.xml'))


#-- EXAMPLE: Setting up the tree view --------------------------------

tree_view = ui.get_object ('tree-view')

tree_view.props.model       = store
tree_view.props.reorderable = True

renderer = gtk.CellRendererToggle ()
TreeViewUtils.enable_renderer_editing (renderer, store, 'is_active')

tree_view.append_column (gtk.TreeViewColumn (None, renderer,
                                             active = store.columns ('is_active')))

renderer = gtk.CellRendererText ()
TreeViewUtils.enable_renderer_editing (renderer, store, 'name')

column = gtk.TreeViewColumn ('Name', renderer,
                             text = store.columns ('name'))
column.set_sort_column_id (store.columns ('name'))
tree_view.append_column (column)
tree_view.set_expander_column (tree_view.get_columns () [-1])

renderer = gtk.CellRendererText ()
TreeViewUtils.enable_renderer_editing (renderer, store, 'description')

column = gtk.TreeViewColumn ('Description', renderer,
                             text = store.columns ('description'))
column.set_sort_column_id (store.columns ('description'))
tree_view.append_column (column)


#-- EXAMPLE: Various tree editing functions --------------------------

def on_create_subtree (*ignored):
    def create_random_children (node, depth):
        for k in range (random.randint (1 if depth == 0 else 0, 3 - depth)):
            child = DefaultTreeNode (Row ('Node %d' % random.randint (100, 1000)))
            create_random_children (child, depth + 1)
            node.child_nodes.append (child)

            if depth == 0:
                tree_view.expand_to_path (child.compute_path ())
                tree_view.expand_row (child.compute_path (), True)

    node = TreeViewUtils.get_selected_node (tree_view)
    create_random_children (node if node is not None else store.root, 0)


def on_insert_new_node (*ignored):
    parent   = TreeViewUtils.get_selected_node (tree_view)
    new_node = DefaultTreeNode (Row ())

    if parent is not None:
        parent.child_nodes.append (new_node)
        tree_view.expand_row (parent.compute_path (), False)
    else:
        store.root.child_nodes.append (new_node)

    tree_view.set_cursor (new_node.compute_path ())


def on_delete_selected (*ignored):
    node = TreeViewUtils.get_selected_node (tree_view)
    if node is not None:
        to_select = (node.next_node or node.previous_node or node.parent_node)
        node.parent_node.child_nodes.remove (node)

        if to_select is not store.root:
            tree_view.set_cursor (to_select.compute_path ())


def on_shuffle (*ignored):
    if warn_if_model_is_sorted ():
        return

    # Note that we cannot directly shuffle node children.
    def shuffle_node (node):
        order = range (node.num_child_nodes)
        random.shuffle (order)
        node.child_nodes.reorder (order)

    node = TreeViewUtils.get_selected_node (tree_view)
    if node is not None:
        shuffle_node (node)
    else:
        for node in tuple (store.root.depth_first_order ()):
            shuffle_node (node)


def warn_if_model_is_sorted ():
    if store.is_sorted:
        message = gtk.MessageDialog (parent = main_window, buttons = gtk.BUTTONS_OK)
        message.props.text       = "<b>Cannot reorder nodes in a sorted model</b>"
        message.props.use_markup = True

        message.run ()
        message.destroy ()

    return store.is_sorted



#-- General UI setup -------------------------------------------------

ui.connect_signals (locals ())

main_window = ui.get_object ('main')
main_window.connect ('destroy', lambda *ignored: gtk.main_quit ())

main_window.show_all ()
main_window.present ()

gtk.main ()



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
