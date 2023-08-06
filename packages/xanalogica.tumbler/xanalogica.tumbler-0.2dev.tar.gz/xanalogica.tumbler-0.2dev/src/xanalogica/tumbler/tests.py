######################################################################
#
# Copyright 2008 Tau Productions Inc. and Contributors.
# All Rights Reserved.
#
# This file is part of the Xanalogica component set.
#
# xanalogica.tumbler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# xanalogica.tumbler is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# xanalogica.tumbler.  If not, see <http://www.gnu.org/licenses/>.
#
######################################################################

import os, re, unittest
import pkg_resources

from zope.testing import doctest, renormalizing

def test_suite():
    global __test__
    __test__ = dict(README=pkg_resources.resource_string(__name__, 'Tumblers.txt'))
    return doctest.DocTestSuite(
             checker=renormalizing.RENormalizing([
               (re.compile('\S+%(sep)s\w+%(sep)s\w+.fs'
                           % dict(sep=os.path.sep)),
                r'/tmp/data/Data.fs'),
               (re.compile('\S+sample-(\w+)'), r'/sample-\1'),
               ]),
             )
