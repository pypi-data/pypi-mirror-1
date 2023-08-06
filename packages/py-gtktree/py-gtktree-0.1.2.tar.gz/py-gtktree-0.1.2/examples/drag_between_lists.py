#! /usr/bin/env python
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

# Demonstrates simple drag'n'drop between two lists of object.  Note that the lists have
# different number of columns, yet it doesn't hinder drag'n'drop at all.
#
# This example also shows that attributes follow normal Python rules: 'python_id' is
# actually a Python property on the row objects (see 'StockItem' class definition).


#-- Importing and other auxiliary stuff ------------------------------

# If standalone, use Py-gtktree from the distribution, not installed.
if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))

try:
    from gtktree.model import RowObjectListStore
    from gtktree.util  import TreeViewUtils
except ImportError:
    sys.exit ("Please build Py-gtktree by executing 'python setup.py build' first")


import gtk


#-- Creating data objects --------------------------------------------

class StockItem (object):

    def __init__(self, id, label):
        self.id          = id
        self.label       = label.replace ('_', '')
        self.__python_id = None

    @property
    def python_id (self):
        if self.__python_id is None:
            for candidate in dir (gtk):
                if 'STOCK_' in candidate and getattr (gtk, candidate) == self.id:
                    self.__python_id = 'gtk.%s' % candidate
                    break
            else:
                self.__python_id = '?'

        return self.__python_id


stock_items = []
for id in gtk.stock_list_ids ():
    data = gtk.stock_lookup (id)
    if data is not None:
        stock_items.append (StockItem (id, data[1]))


#-- EXAMPLE: Creating the tree models --------------------------------

select_from    = RowObjectListStore ([(str, 'id'),
                                      (str, 'label')],
                                     stock_items)
selected_items = RowObjectListStore ([(str, 'id'),
                                      (str, 'python_id'),
                                      (str, 'label')])


#-- Loading UI definition --------------------------------------------

ui = gtk.Builder ()
ui.add_from_file (os.path.join (os.path.dirname (sys.argv[0]), 'drag_between_lists.ui.xml'))


#-- EXAMPLE: Setting up the tree views -------------------------------

selected_items_view = ui.get_object ('selected-items-view')

selected_items_view.props.model = selected_items

selected_items_view.append_column (gtk.TreeViewColumn (None, gtk.CellRendererPixbuf (),
                                                       stock_id = selected_items.columns ('id')))
selected_items_view.append_column (gtk.TreeViewColumn ('Label', gtk.CellRendererText (),
                                                       text = selected_items.columns ('label')))
selected_items_view.append_column (gtk.TreeViewColumn ('ID', gtk.CellRendererText (),
                                                       text = selected_items.columns ('id')))
selected_items_view.append_column (gtk.TreeViewColumn ('Python ID', gtk.CellRendererText (),
                                                       text = selected_items.columns ('python_id')))


select_from_view = ui.get_object ('select-from-view')

select_from_view.props.model = select_from

select_from_view.append_column (gtk.TreeViewColumn (None, gtk.CellRendererPixbuf (),
                                                    stock_id = select_from.columns ('id')))
select_from_view.append_column (gtk.TreeViewColumn ('Label', gtk.CellRendererText (),
                                                    text = select_from.columns ('label')))


#-- EXAMPLE: Enabling drag'n'drop ------------------------------------

# By default, drag'n'drop between models is possible only if they have equal and non-None
# 'object_type' value.  Refer to RowObjectTreeModel.is_accepting_drags_from()
# documentation for details.
select_from   .object_type = StockItem
selected_items.object_type = StockItem

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
