#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2006 Emencia
#
# Authors:
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
# $Id: cleansources.py 488 2006-11-08 16:26:13Z tarek $

import os
import sys
import unittest

dirname = os.path.dirname(__file__)
if dirname not in sys.path:
    sys.path.append(os.path.split(dirname)[0])

#from emencia.ecscart import Rules
from ecs.cart.tests import database

class RulesTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


def test_suite():
    tests = [unittest.makeSuite(RulesTest)]
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.main()
