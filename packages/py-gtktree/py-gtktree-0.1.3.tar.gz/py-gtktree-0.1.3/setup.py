#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Py-gtktree.
#
# Unlike the rest of Py-gtktree, it is explicitely put in Public Domain.  Use as you
# please.


from __future__ import with_statement

REQUIRED_PYTHON_VERSION = (2, 5)


import sys
import os
import re


if sys.version_info[:3] < REQUIRED_PYTHON_VERSION:
    sys.exit ('%s: Python version %s is required'
              % (sys.argv[0],
                 '.'.join (str (subversion) for subversion in REQUIRED_PYTHON_VERSION)))



if os.path.dirname (sys.argv[0]):
    os.chdir (os.path.dirname (sys.argv[0]))

expected_file = os.path.join ('gtktree', 'model.py')
if not os.path.isfile (expected_file):
    sys.exit ("%s: cannot find '%s', strange..." % (sys.argv[0], expected_file))



try:
    with open ('version') as version_file:
        version = version_file.readline ().strip ()
except IOError:
    sys.exit ('%s: error: %s' % (sys.argv[0], sys.exc_info () [1]))



def configure (version):
    configuration_lines      = []
    configuration_parameters = { 'version_string': version,
                                 'version':        tuple (int (subversion)
                                                          for subversion in version.split ('.')) }


    with open (os.path.join ('gtktree', '__init__.py.in')) as template_file:
        in_configuration = False

        for line in template_file:
            special_line = re.search ('# *(/?)CONFIGURATION *$', line)
            if special_line:
                in_configuration = (not special_line.group (1))
            else:
                if in_configuration:
                    line = line % configuration_parameters

                configuration_lines.append (line)

    try:
        with open (os.path.join ('gtktree', '__init__.py'), 'r') as output_file_in:
            if output_file_in.readlines () == configuration_lines:
                return
    except IOError:
        # Ignore and assume it is not there.  Real errors will be catched when writing.
        pass

    try:
        with open (os.path.join ('gtktree', '__init__.py'), 'w') as output_file_out:
            output_file_out.writelines (configuration_lines)
    except IOError:
        sys.exit (str (sys.exc_info () [1]))



configure (version)



from distutils.core import setup


long_description = \
"""
Py-gtktree is a collection of utilities for building trees with PyGTK.  Currently it
includes custom Pythonic implementations of gtk.TreeModel interface.
"""

classifiers = ['Topic :: Software Development :: Libraries :: Python Modules',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
               'Development Status :: 3 - Alpha',  # Now with tree store, but too untested.
               'Operating System :: OS Independent',
               'Programming Language :: Python']


setup (name             = 'py-gtktree',
       version          = version,
       description      = 'A collection of utilities for building trees with PyGTK',
       long_description = long_description,
       author           = 'Paul Pogonyshev',
       author_email     = 'py-gtktree@lists.launchpad.net',
       url              = 'https://launchpad.net/py-gtktree',
       download_url     = 'https://launchpad.net/py-gtktree/+download',
       license          = 'GNU Lesser General Public License v3',
       classifiers      = classifiers,
       packages         = ['gtktree', 'gtktree._impl'])



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
