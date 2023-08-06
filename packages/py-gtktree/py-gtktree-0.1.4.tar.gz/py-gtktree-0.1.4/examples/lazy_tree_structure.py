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

# Demonstrates lazy tree structure loading/creation.  Additionally, all nodes initially
# claim to have children, to show that 'LazyDefaultTreeNode' is capable of properly
# working in situation where a node that appears to have children turns out to have none.


#-- Importing and other auxiliary stuff ------------------------------

from __future__ import with_statement

# If standalone, use Py-gtktree from the distribution, not installed.
if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))

try:
    from gtktree.model import RowObjectTreeStore, DefaultTreeNode, LazyDefaultTreeNode
except ImportError:
    sys.excepthook (*sys.exc_info ())
    sys.exit ("Please build Py-gtktree by executing 'python setup.py build' first")


import os

import gtk



#-- EXAMPLE: Defining row object class -------------------------------

class Folder (object):

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename (path)

    # Note that we claim all nodes to have children.  This is not required.  If this
    # overriden method is removed, tree model will load one additional structural level to
    # find out if there actually are child nodes.  In such case model loading will be
    # considerably slower, though more correct from user point of view.  So, whether to
    # behave like this is a tradeoff between speed and user experience.
    def lazy_has_children (self):
        return True

    # We are not required to return a list.  We can return any iterable of nodes or even
    # override with a generator function, as demonstrated.  In fact, we can even return
    # not nodes, but row objects --- those will be wrapped in nodes for us.
    def lazy_load (self):
        print 'loading %s...' % self.path
        for entry in sorted (name for name in os.listdir (self.path) if not name.startswith ('.')):
            subpath = os.path.join (self.path, entry)
            if os.path.isdir (subpath):
                yield Folder (subpath)


#-- EXAMPLE: Creating the tree model ---------------------------------

contents = RowObjectTreeStore ([(str, 'name')],
                               [LazyDefaultTreeNode (Folder (os.path.expanduser ('~')))])


#-- Loading UI definition --------------------------------------------

ui = gtk.Builder ()
ui.add_from_file (os.path.join (os.path.dirname (sys.argv[0]), 'lazy_tree_structure.ui.xml'))


#-- EXAMPLE: Setting up the tree view --------------------------------

file_system_view = ui.get_object ('file-system-view')

file_system_view.props.model = contents

file_system_view.append_column (gtk.TreeViewColumn ('Name', gtk.CellRendererText (),
                                                    text = contents.columns ('name')))


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
