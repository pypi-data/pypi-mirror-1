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

# Demonstrates creation of a simple RowObjectTreeStore containing a tree representation of
# an XML file.  It is possible to change parsed file at runtime, so there is a minimum of
# tree modification (contents replacement) as well.
#
# Note that you cannot put anything into a RowObjectTreeStore, unlike in a list store.
# However, you can wrap any object with a DefaultTreeNode.  Nodes are used to build tree
# structure and are needed since there is no standardized way of building trees.


#-- Importing and other auxiliary stuff ------------------------------

# If standalone, use Py-gtktree from the distribution, not installed.
if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))

try:
    from gtktree.model import RowObjectTreeStore, DefaultTreeNode
except ImportError:
    sys.excepthook (*sys.exc_info ())
    sys.exit ("Please build Py-gtktree by executing 'python setup.py build' first")


import gtk
import os.path
import sys
from xml.dom import minidom, Node


#-- EXAMPLE: Creating the tree model ---------------------------------

def get_dom_node_value (dom_node):
    if dom_node.nodeValue:
        return dom_node.nodeValue

    if len (dom_node.childNodes) == 1 and dom_node.firstChild.nodeType == Node.TEXT_NODE:
        return dom_node.firstChild.nodeValue

def get_dom_attributes (dom_node):
    attributes = ''
    for name, value in dict (dom_node.attributes).items ():
        attributes += ' %s="%s"' % (name, value.nodeValue)

    return attributes[1:]

store = RowObjectTreeStore ([(str, 'nodeName'),
                             (str, get_dom_node_value),
                             (str, get_dom_attributes)])


#-- EXAMPLE: Populating the tree model -------------------------------

def build_tree_node (dom_node):
    return DefaultTreeNode (dom_node,
                            [build_tree_node (child) for child in dom_node.childNodes
                             if child.nodeType != Node.TEXT_NODE])

def fill_store (filename):
    store.root.child_nodes = [build_tree_node (minidom.parse (filename).documentElement)]

ui_file_name = os.path.join (os.path.dirname (sys.argv[0]), 'simple_tree.ui.xml')


#-- Loading UI definition --------------------------------------------

ui = gtk.Builder ()
ui.add_from_file (ui_file_name)


#-- EXAMPLE: Setting up the tree view --------------------------------

xml_tree_view = ui.get_object ('xml-tree-view')

xml_tree_view.props.model = store

xml_tree_view.append_column (gtk.TreeViewColumn ('Name', gtk.CellRendererText (),
                                                 text = store.columns ('nodeName')))

xml_tree_view.append_column (gtk.TreeViewColumn ('Attributes', gtk.CellRendererText (),
                                                 text = store.columns (get_dom_attributes)))

xml_tree_view.append_column (gtk.TreeViewColumn ('Text Value', gtk.CellRendererText (),
                                                 text = store.columns (get_dom_node_value)))


#-- Handle interaction between file chooser and the tree view --------

xml_chooser = ui.get_object ('xml-chooser')

def on_file_chosen (*ignored):
    fill_store (xml_chooser.get_filename ())
    xml_tree_view.expand_all ()

# Initialize.
xml_chooser.set_filename (ui_file_name)
fill_store (ui_file_name)
xml_tree_view.expand_all ()


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
