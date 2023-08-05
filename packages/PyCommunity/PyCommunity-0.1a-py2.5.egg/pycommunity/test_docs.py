#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 Tarek Ziadé <tarek@ziade.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# $Id: addheaders.py 448 2006-10-31 13:31:30Z tarek $
import doctest
import unittest
import os

flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_ONLY_FIRST_FAILURE)

files = [os.path.join('doc', filename) for filename in os.listdir('doc')
         if filename.endswith('.txt')]

def cleanup():
    top = os.path.join(os.path.dirname(__file__), 'tests/www')
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def test_suite():
    cleanup()
    suite = []
    for testfile in files:
        suite.append(doctest.DocFileTest(testfile, optionflags=flags))
    return unittest.TestSuite(suite)

if __name__ == '__main__':
    try:
        unittest.main(defaultTest='test_suite')
        # XXX todo: use setup teardown
    finally:
        cleanup()

    
