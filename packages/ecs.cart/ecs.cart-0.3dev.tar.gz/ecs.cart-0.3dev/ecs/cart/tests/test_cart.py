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

from ecs.cart import Cart
from ecs.cart.tests import database

class CartTest(unittest.TestCase):

    def setUp(self):
        Cart._sqluri_callback = database

    def test_add_del_product(self):
        cart = Cart('user_test_1')

        cart.add_product('cheeseburger', 3.50)
        cart.add_product('coca light', price='1.4', quantity=1)
        cart.add_product('glace', price=4, vat=19.6, quantity='3')

        self.assertEquals(cart.products['cheeseburger']['quantity'], 1)
        self.assertEquals(cart.products['coca light']['price']['included_tax'], 1.4)
        self.assertEquals(cart.products['coca light']['price']['vat'], 0.0)
        self.assertEquals(cart.products['glace']['quantity'], 3)
        self.assertEquals(cart.products['glace']['price']['vat'], 19.6)
        self.assertRaises(ValueError, cart.add_product)

        cart.del_product('cheeseburger')
        cart.del_product('coca light')
        cart.del_product('fantaisic object')

        self.assertRaises(ValueError,
                          cart.get_product_property, 'cheesebuger',
                          'price')
        self.assertRaises(ValueError,
                          cart.get_product_property, 'coca light',
                          'quantity')
        self.assertEquals(cart.get_product_property('glace',
                          'quantity'), 3)
        cart.del_all_product()

    def test_set_quantity(self):
        cart = Cart('user_test_2')

        cart.add_product('cheeseburger', 3.50)
        cart.set_quantity('cheeseburger', 10)

        self.assertEquals(cart.get_product_property('cheeseburger',
                          'quantity'), 10)
        self.assertRaises(ValueError, cart.set_quantity,
                          'fantaisic object', 42)

        cart.set_quantity('cheeseburger', 0)
        self.assertRaises(ValueError,
                          cart.get_product_property, 'cheeseburger',
                          'quantity')
        cart.del_all_product()

    def test_get_cart_amount(self):
        cart = Cart('user_test_3')

        cart.add_product('sauce', price=0.42, quantity=10)
        cart.add_product('frite', price=1.50, quantity=20)
        cart.add_product('cheeseburger', price=3.50, quantity=20)

        self.assertEquals(cart.get_cart_amount(), 104.2)
        cart.del_all_product()


#    def test_persistence(self):
#        cart = Cart('user_test_4')
#
#        self.assertEquals(cart.products, {})
#        cart.add_product('cheeseburger', 3.50)
#        cart.add_product('coca light', 1.4)
#        cart.add_product('glace', 4)
#        cart.validation('ok')
#
#        reloaded_cart = Cart('user_test_4')
#        self.assertEquals(reloaded_cart.products,
#                          {u'coca light': {'price' : {u'included_tax' :
#                                                      1.3999999999999999,
#                                                      u'vat' : 0.0,
#                                                      u'amount_vat' : 0.0,
#                                                      u'without_tax' :
#                                                      1.3999999999999999},
#                           u'quantity' : 1.0},
#                           u'cheeseburger': {'price' : {u'included_tax' :
#                                                        3.5,
#                                                        u'vat' : 0.0,
#                                                        u'amount_vat' : 0.0,
#                                                        u'without_tax' :
#                                                        3.5},
#                                             u'quantity' : 1.0},
#                           u'glace': {'price' : {u'included_tax' : 4.0,
#                                                 u'vat' : 0.0,
#                                                 u'amount_vat' : 0.0,
#                                                 u'without_tax' : 4.0},
#                                      u'quantity' : 1.0}})
#
#        cart.del_all_product()

def test_suite():
    tests = [unittest.makeSuite(CartTest)]
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.main()
