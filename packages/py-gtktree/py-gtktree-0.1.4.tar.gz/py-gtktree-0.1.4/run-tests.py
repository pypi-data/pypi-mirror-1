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
import unittest


if os.path.dirname (sys.argv[0]):
    os.chdir (os.path.dirname (sys.argv[0]))

expected_file = os.path.join ('gtktree', 'model.py')
if not os.path.isfile (expected_file):
    sys.exit ("%s: cannot find '%s', strange..." % (sys.argv[0], expected_file))


_configured = False

try:
    import gtktree

    # The following test is needed to avoid testing an installed version in preference to
    # unconfigured distribution.
    gtktree_path = os.path.abspath ('gtktree')
    _configured  = (gtktree   .__file__ == os.path.join (gtktree_path, '__init__.py')
                    or gtktree.__file__ == os.path.join (gtktree_path, '__init__.pyc'))

    if not _configured:
        del gtktree
        del sys.modules['gtktree']

except ImportError:
    pass

if not _configured:
    print "Detected an unconfigured source tree, trying to configure first..."

    arguments = sys.argv
    sys.argv = [arguments[0], '--obsoletes']
    import setup
    sys.argv = arguments



_extensions_built = False

def _build_extensions ():
    global _extensions_built

    if not _extensions_built:
        print ('Building extension...')

        # FIXME: Is that portable enough?
        if os.system ('python setup.py build_ext') != 0:
            sys.exit (1)

        _extensions_built = True



_TEST_MODULES = ('list_store', 'tree_store')


def _import_module (module_name):
    _build_extensions ()
    return __import__('test.%s' % module_name, globals (), locals (), ('*',))

def _import_module_tests (module_name):
    return unittest.defaultTestLoader.loadTestsFromModule (_import_module (module_name))

def _import_all_tests ():
    everything = unittest.TestSuite ()
    for module_name in _TEST_MODULES:
        everything.addTest (_import_module_tests (module_name))

    return everything


class _TestModuleImporter (object):

    def __init__(self, module_name):
        self._module_name = module_name

    def __call__(self):
        return _import_module_tests (object.__getattribute__(self, '_module_name'))

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr (_import_module (object.__getattribute__(self, '_module_name')), name)


class AllTests (object):

    def __init__(self):
        self.everything = _import_all_tests
        for module_name in _TEST_MODULES:
            setattr (self, module_name, _TestModuleImporter (module_name))


class TestProgram (unittest.TestProgram):

    def runTests (self):
        _build_extensions ()
        unittest.TestProgram.runTests (self)



TestProgram (AllTests (), 'everything')



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
