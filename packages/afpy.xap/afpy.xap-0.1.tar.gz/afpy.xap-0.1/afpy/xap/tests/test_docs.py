#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 Tarek Ziadé
#
# Authors:
#   Tarek Ziadé <tarek@ziade.org>
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
import doctest
import unittest
import sys
import os

current_dir = os.path.dirname(__file__)
if current_dir == '':
    current_dir = '.'

abs_path = os.path.abspath(current_dir)

if current_dir not in sys.path:
    sys.path.append(os.path.split(current_dir)[0])

# patching settings
import settings
settings.SQLURI = 'sqlite:///%s/data/base.sql3' % abs_path

def doc_suite(test_dir, setUp=None, tearDown=None, globs=None):
    """returns a test suite, based on docs"""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    product_dir = os.path.split(test_dir)[0]
    if product_dir not in sys.path:
        sys.path.append(product_dir)

    doc_dir = os.path.join(product_dir, 'doc')
    #docs = [os.path.join(doc_dir, doc) for doc in
    #        os.listdir(doc_dir) if doc.endswith('.txt')]
    docs = [os.path.join(doc_dir, doc) for doc in
            os.listdir(doc_dir) if doc.endswith('.txt')]

    for test in docs:
        suite.append(doctest.DocFileTest(test,
                     optionflags=flags, globs=globs,
                     setUp=setUp, tearDown=tearDown,
                     module_relative=False))

    return unittest.TestSuite(suite)


def test_suite():
    globs = globals()

    return doc_suite(current_dir, globs=globs)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

