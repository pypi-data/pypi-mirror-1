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


__all__ = ('Foo',
           'PopAllList')



class Foo (object):

    __slots__ = ('foo', 'bar')

    def __init__(self, foo, bar = None):
        self.foo = foo
        self.bar = bar

    def __eq__(self, other):
        return self.foo == other.foo and self.bar == other.bar

    def __ne__(self, other):
        return self.foo != other.foo or self.bar != other.bar

    def __repr__(self):
        if self.bar is not None:
            return '%s(%s, %s)' % (self.__class__.__name__, self.foo, self.bar)
        else:
            return '%s(%s)' % (self.__class__.__name__, self.foo)



class PopAllList (list):

    def pop_all (self):
        result = self[:]
        del self[:]
        return result



# Local variables:
# mode: python
# python-indent: 4
# indent-tabs-mode: nil
# fill-column: 90
# End:
