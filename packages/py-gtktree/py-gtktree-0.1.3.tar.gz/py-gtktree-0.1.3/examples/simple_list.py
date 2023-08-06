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

# Demonstrates creation of a simple RowObjectListStore containing list of imported Python
# objects.  Note how you can use anything as row objects in an RowObjectListStore: there
# are no restriction.  You only need to make sure attributes are compatible with your row
# objects.
#
# To emphasize that RowObjectListStore currently does _not_ implement gtk.TreeSortable, we
# explicitly make it sortable using the standard wrapper --- gtk.TreeModelSort.


#-- Importing and other auxiliary stuff ------------------------------

# If standalone, use Py-gtktree from the distribution, not installed.
if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))

try:
    from gtktree.model import RowObjectListStore
except ImportError:
    sys.exit ("Please build Py-gtktree by executing 'python setup.py build' first")


import gtk
import os.path
import sys


#-- EXAMPLE: Creating the tree model ---------------------------------

def get_module_file (module):
    return module.__file__ if hasattr (module, '__file__') else None

def get_module_version (module):
    return module.__version__ if hasattr (module, '__version__') else None

modules = (module for module in sys.modules.values () if module is not None)
store   = RowObjectListStore ([(str, '__name__'),
                               (str, get_module_file),
                               (str, get_module_version)],
                              modules)


#-- Loading UI definition --------------------------------------------

ui = gtk.Builder ()
ui.add_from_file (os.path.join (os.path.dirname (sys.argv[0]), 'simple_list.ui.xml'))


#-- EXAMPLE: Setting up the tree view --------------------------------

modules_view = ui.get_object ('modules-view')

modules_view.props.model = gtk.TreeModelSort (store)

column = gtk.TreeViewColumn ('Name', gtk.CellRendererText (),
                             text = store.columns ('__name__'))
column.set_sort_column_id (store.columns ('__name__'))
modules_view.append_column (column)

column = gtk.TreeViewColumn ('Loaded From', gtk.CellRendererText (),
                             text = store.columns (get_module_file))
column.set_sort_column_id (store.columns (get_module_file))
modules_view.append_column (column)

column = gtk.TreeViewColumn ('Version', gtk.CellRendererText (),
                             text = store.columns (get_module_version))
column.set_sort_column_id (store.columns (get_module_version))
modules_view.append_column (column)


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
