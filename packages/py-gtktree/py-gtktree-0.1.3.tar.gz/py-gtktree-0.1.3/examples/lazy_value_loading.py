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

# Demonstrates lazy loading of individual values in a list.  Uses several methods in
# TreeViewUtils to watch and retrieve set of currently visible rows.  Adds a random delay
# before a value is loaded to make loading visible and emulate some slow connection.


#-- Importing and other auxiliary stuff ------------------------------

from __future__ import with_statement

# If standalone, use Py-gtktree from the distribution, not installed.
if __name__ == '__main__':
    import os, sys
    sys.path.insert (0, os.path.join (sys.path[0], os.pardir))

try:
    from gtktree.model import RowObjectListStore
    from gtktree.util  import TreeViewUtils
except ImportError:
    sys.exit ("Please build Py-gtktree by executing 'python setup.py build' first")


import mimetypes
import os, os.path
import random
import re

import gobject
import gtk
import pango


#-- EXAMPLE: Defining row object class -------------------------------

class DirectoryEntry (object):

    def __init__(self, name, directory):
        self.name             = name
        self.directory        = directory
        self.mime_type        = None
        self.contents_preview = None
        self.__timeout_id     = None

    @property
    def loading (self):
        return self.__timeout_id is not None

    def lazy_load (self, model, iter):
        if self.loading or self.mime_type is not None or self.name == '..':
            return

        model.note_changes (iter)

        change_loading_status (+1)
        # This is only to make loading appear more 'visually interesting'.
        self.__timeout_id = gobject.timeout_add (random.randint (250, 3000),
                                                 self._do_lazy_load, model, iter)

    def abort_lazy_loading (self):
        if self.loading:
            change_loading_status (-1)
            gobject.source_remove (self.__timeout_id)
            self.__timeout_id = None

    def _do_lazy_load (self, model, iter):
        if not self.directory:
            self.mime_type = mimetypes.guess_type (self.name) [0]
            if self.mime_type is None:
                self.mime_type = '?'

            with open (self.name) as file:
                self.contents_preview = re.sub ('\\s+', ' ', file.read (50)).decode ('utf-8', 'replace')
                if file.read (1):
                    self.contents_preview += '...'
        else:
            self.mime_type = ''
            for directory_name, subdirectories, filenames in os.walk (self.name):
                self.contents_preview = '%d subfolder(s), %d file(s)' % (len (subdirectories),
                                                                         len (filenames))
                del subdirectories[:]

        model.note_changes (iter)
        change_loading_status (-1)
        self.__timeout_id = None
        return False


#-- EXAMPLE: Creating the tree model ---------------------------------

def get_icon_stock_id (entry):
    if entry.directory:
        return gtk.STOCK_DIRECTORY if entry.name != '..' else None
    else:
        return gtk.STOCK_FILE

def is_loaded (entry):
    return not entry.loading

contents = RowObjectListStore ([(str,  get_icon_stock_id),
                                (str,  'name'),
                                (str,  'mime_type'),
                                (str,  'contents_preview'),
                                (bool, is_loaded),
                                (bool, 'loading')])


#-- Loading UI definition --------------------------------------------

ui = gtk.Builder ()
ui.add_from_file (os.path.join (os.path.dirname (sys.argv[0]), 'lazy_value_loading.ui.xml'))


#-- EXAMPLE: Setting up the tree view --------------------------------

contents_view = ui.get_object ('contents-view')

contents_view.props.model = contents

contents_view.append_column (gtk.TreeViewColumn (None, gtk.CellRendererPixbuf (),
                                                 stock_id = contents.columns (get_icon_stock_id)))
contents_view.append_column (gtk.TreeViewColumn ('Name', gtk.CellRendererText (),
                                                 text = contents.columns ('name')))
contents_view.append_column (gtk.TreeViewColumn ('MIME Type', gtk.CellRendererText (),
                                                 text = contents.columns ('mime_type')))

column         = gtk.TreeViewColumn ('Contents')
entry_contents = gtk.CellRendererText ()
loading        = gtk.CellRendererText ()

column.pack_start (entry_contents)
column.add_attribute (entry_contents, 'text',    contents.columns ('contents_preview'))
column.add_attribute (entry_contents, 'visible', contents.columns (is_loaded))

column.pack_start (loading)
loading.props.text  = 'Loading...'
loading.props.style = pango.STYLE_ITALIC
column.add_attribute (loading, 'visible', contents.columns ('loading'))

contents_view.append_column (column)


#-- Listing directory contents ---------------------------------------

directory_name_label = ui.get_object ('directory-name-label')

def enter_directory (name):
    os.chdir (name)
    directory_name_label.props.label = '<b>%s</b>' % gobject.markup_escape_text (os.getcwd ())

    for entry in contents:
        entry.abort_lazy_loading ()

    contents.clear ()
    if os.path.split (os.getcwd ()) [1]:
        contents.append (DirectoryEntry ('..', True))

    for directory_name, subdirectories, filenames in os.walk ('.'):
        subdirectories.sort ()
        for subdirectory in subdirectories:
            if not subdirectory.startswith ('.'):
                contents.append (DirectoryEntry (subdirectory, True))

        filenames.sort ()
        for filename in filenames:
            if not filename.startswith ('.'):
                contents.append (DirectoryEntry (filename, False))

        # Don't recurse anything.
        del subdirectories[:]

    contents_view.set_cursor ((0,))


enter_directory ('.')


#-- EXAMPLE: Handling 'row-activated' signal -------------------------

def on_contents_view_row_activated (directory_view, path, column):
    entry = contents[contents.get_iter (path)]
    if entry.directory:
        enter_directory (entry.name)


#-- EXAMPLE: Hooking up lazy loading of visible rows -----------------

def load_visible_entries (contents_view):
    for iter, entry in TreeViewUtils.get_viewport_rows (contents_view):
        entry.lazy_load (contents, iter)

TreeViewUtils.connect_viewport_handler (contents_view, load_visible_entries)


num_loading_operations = 0
loading_status_label   = ui.get_object ('loading-status-label')

def change_loading_status (delta):
    global num_loading_operations

    num_loading_operations += delta

    if num_loading_operations > 0:
        loading_status_label.props.label = \
            'Loading operations in progress: %d (slowness is artificial)' % num_loading_operations
    else:
        loading_status_label.props.label = ''


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
