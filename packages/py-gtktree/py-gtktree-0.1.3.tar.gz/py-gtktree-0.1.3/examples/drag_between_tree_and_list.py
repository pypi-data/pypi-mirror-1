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


#-- Importing and other auxiliary stuff ------------------------------

# If standalone, use Py-gtktree from the distribution, not installed.
if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))

try:
    from gtktree.model import RowObjectListStore, RowObjectTreeStore, DefaultTreeNode
    from gtktree.util  import TreeViewUtils
except ImportError:
    sys.exit ("Please build Py-gtktree by executing 'python setup.py build' first")


import gtk
import pango


#-- EXAMPLE: Defining row object classes -----------------------------

class FoodCategory (object):

    def __init__(self, name):
        self.name = name

    @property
    def display_font_weight (self):
        return pango.WEIGHT_BOLD

    # This property will be picked up by tree node with duck typing.
    @property
    def is_draggable (self):
        return False


class FoodItem (object):

    def __init__(self, category, name):
        self.category = category
        self.name     = name

    @property
    def display_font_weight (self):
        return pango.WEIGHT_NORMAL

    # The following methods will be picked up by tree node with duck typing.

    def accepts_dragged_child_node (self, child_node):
        return False

    def accepts_parent_node_after_drag (self, parent_node):
        return self.category is parent_node.row_object


#-- Defining available for selection data ----------------------------

fruits     = FoodCategory ('Fruits')
vegetables = FoodCategory ('Vegetables')
categories = [fruits, vegetables]
food_items = [FoodItem (fruits, 'Apple'),
              FoodItem (fruits, 'Grape'),
              FoodItem (fruits, 'Lemon'),
              FoodItem (vegetables, 'Tomato'),
              FoodItem (vegetables, 'Cucumber'),
              FoodItem (vegetables, 'Carrot')]


#-- EXAMPLE: Creating the tree models --------------------------------

select_from = RowObjectTreeStore ([(str, 'name'),
                                   (int, 'display_font_weight')],
                                  (DefaultTreeNode (category,
                                                    (DefaultTreeNode (item)
                                                     for item in food_items
                                                     if item.category is category))
                                   for category in categories))

selected_items = RowObjectListStore ([(str, 'name'),
                                      (str, 'category.name')])


#-- Loading UI definition --------------------------------------------

ui = gtk.Builder ()
ui.add_from_file (os.path.join (os.path.dirname (sys.argv[0]),
                                'drag_between_tree_and_list.ui.xml'))


#-- EXAMPLE: Setting up the tree views -------------------------------

selected_items_view = ui.get_object ('selected-items-view')

selected_items_view.props.model = selected_items

selected_items_view.append_column (gtk.TreeViewColumn ('Name', gtk.CellRendererText (),
                                                       text = selected_items.columns ('name')))
selected_items_view.append_column (gtk.TreeViewColumn ('Category', gtk.CellRendererText (),
                                                       text = selected_items.columns ('category.name')))


select_from_view = ui.get_object ('select-from-view')

select_from_view.props.model = select_from
select_from_view.expand_all ()

select_from_view.append_column (gtk.TreeViewColumn
                                (None, gtk.CellRendererText (),
                                 text   = select_from.columns ('name'),
                                 weight = select_from.columns ('display_font_weight')))


#-- EXAMPLE: Enabling drag'n'drop ------------------------------------

# By default, drag'n'drop between models is possible only if they have equal and non-None
# 'object_type' value.  Refer to RowObjectTreeModel.is_accepting_drags_from()
# documentation for details.
select_from   .object_type = FoodItem
selected_items.object_type = FoodItem

TreeViewUtils.enable_standard_drags (selected_items_view)
TreeViewUtils.enable_standard_drags (select_from_view)


#-- General UI setup -------------------------------------------------

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
