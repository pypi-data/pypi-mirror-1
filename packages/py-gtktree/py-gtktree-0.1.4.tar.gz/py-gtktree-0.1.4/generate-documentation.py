#! /usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------#
# This file is part of Py-gtktree.                                         #
#                                                                          #
# Copyright (C) 2007, 2008, 2009 Paul Pogonyshev.                          #
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


import os
import sys
import re

from urlparse import urlunsplit


if os.path.dirname (sys.argv[0]):
    os.chdir (os.path.dirname (sys.argv[0]))

expected_file = os.path.join ('gtktree', 'model.py')
if not os.path.isfile (expected_file):
    sys.exit ("%s: cannot find '%s', strange..." % (sys.argv[0], expected_file))


try:
    from docutils.core import publish_cmdline
except ImportError:
    sys.exit ("%s: docutils not found; get them from http://docutils.sourceforge.net/"
              % sys.argv[0])


input_file_name  = os.path.join ('docs', 'py-gtktree.txt')
output_file_name = os.path.join ('docs', 'py-gtktree.html')

sys.argv.extend (['--stylesheet-path=%s' % os.path.join ('docs', 'reST.css'),
                  '--embed-stylesheet',
                  '--no-source-link',
                  '--strip-comments',
                  '--language=en',
                  '--input-encoding=utf-8:strict',
                  '--output-encoding=utf-8:strict',
                  '--no-file-insertion',
                  input_file_name, output_file_name])


publish_cmdline (writer_name = 'html', description = 'Generate Py-gtktree documentation')


sys.stdout.write ("Documentation has been generated as file '%s'\n" % output_file_name)
sys.stdout.write ("Point your browser to %s\n"
                  % urlunsplit (('file', None, os.path.abspath (output_file_name), None, None)))



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
