#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2006 Emencia
#
#
# Authors: Tarek Ziade <tarek@emencia.com>
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
# $Id: test_docs.py 1110 2007-02-14 08:43:34Z tarek $
import doctest
import unittest
import sys
import os

from emencia.ecsutils.tests.ecstests import doc_suite

current_dir = os.path.dirname(__file__)

from emencia.ecsdb.tests.patchdb import apply, unapply
from emencia.ecsdbtables.tests import fixture
from inject_data import inject_test_data

globs = globals()
globs['doc_path'] = os.path.join(current_dir, '..', 'doc')

def setUp(context):
    apply(context)
    inject_test_data()

def tearDown(context):
    unapply(context)

def test_suite():
    return doc_suite(current_dir, setUp, tearDown, globs=globs)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

