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



import subprocess

from distutils                   import log
from distutils.core              import setup, Extension
from distutils.command.build_ext import build_ext as _build_ext
from distutils.command.clean     import clean as _clean


# Symlink built extension into the main source code tree.  This allows to run examples
# just from a built distribution, without installing first.
class build_ext (_build_ext):

    def build_extension (self, extension):
        _build_ext.build_extension (self, extension)

        if not self.inplace and os.name == 'posix':
            filename        = self.get_ext_filename (extension.name)
            link_filename   = filename
            target_filename = os.path.join (self.build_lib, filename)

            recursion_scan  = os.path.split (filename) [0]

            if hasattr (os, 'symlink'):
                if (os.path.islink (link_filename)
                    and os.path.realpath (link_filename) == os.path.abspath (target_filename)):
                    return

            while recursion_scan:
                recursion_scan  = os.path.split (recursion_scan) [0]
                target_filename = os.path.join  (os.pardir, target_filename)

            try:
                os.remove (link_filename)
            except:
                # Ignore all errors.
                pass

            if hasattr (os, 'symlink'):
                try:
                    os.symlink (target_filename, link_filename)
                except:
                    # Ignore all errors.
                    pass
            else:
                # FIXME: Copy the library then.
                pass


class clean (_clean):

    def run (self):
        _clean.run (self)

        if not self.build_lib:
            return

        build_lib = os.path.abspath (self.build_lib)
        for dirpath, dirnames, filenames in os.walk ('gtktree'):
            for filename in filenames:
                filename = os.path.join (dirpath, filename)
                if os.path.islink (filename):
                    links_to = os.path.abspath (os.path.join (dirpath, os.readlink (filename)))
                    if links_to.startswith (build_lib):
                        try:
                            log.info ("removing '%s'", filename)
                            os.remove (filename)
                        except IOError, exception:
                            sys.stderr.write ("warning: %s\n" % exception.message)



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


def invoke_pkg_config (*arguments):
    popen  = subprocess.Popen (['pkg-config'] + list (arguments),
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE)
    result = popen.communicate ()

    if result[1]:
        sys.exit (result[1])
    elif popen.returncode != 0:
        raise ValueError ("unknown pkg-config failure")

    return [part for part in result[0].strip ().split (' ') if part]


c_hacks_extension = Extension (
    name               = 'gtktree._impl.c_hacks',
    sources            = [os.path.join ('gtktree', '_impl', 'c_hacks.c')],
    extra_compile_args = invoke_pkg_config ('--cflags', 'gtk+-2.0', 'pygobject-2.0'),
    extra_link_args    = invoke_pkg_config ('--libs',   'gtk+-2.0', 'pygobject-2.0'))


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
       packages         = ['gtktree', 'gtktree._impl'],
       ext_modules      = [c_hacks_extension],
       cmdclass         = { 'build_ext': build_ext,
                            'clean':     clean })



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
