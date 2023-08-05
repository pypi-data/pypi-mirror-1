# (C) Copyright 2007 Nuxeo SAS <http://nuxeo.com>
# Author: bdelbosc
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#
"""Test Plush

$Id: test_plush.py 51222 2007-02-22 09:18:53Z bdelbosc $
"""
import sys
import os
import unittest
import doctest

def fixIncludePath():
    """Add .. to the path"""
    module_path = os.path.join(os.path.dirname(__file__), "..")
    sys.path.insert(0, os.path.normpath(module_path))
fixIncludePath()


def test_suite():
    """Return a test suite."""
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite("test_plush.txt"))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
