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

"""Cart module for ecscart"""

#from emencia.ecsdb.persistency import PersistentClass
from price import Price
from rules.rules_config import RulesInit

class Cart(object):
    """Cart object to manage an user caddy"""
    products = {}
    cart_reference = None
    validation_statut = None
    _update = False

    #__metaclass__ = PersistentClass

    def __init__(self, reference=None, rules_conf=None):
        """Instantiate the cart"""
        self.rules = RulesInit(conf_file=rules_conf)
        if reference is not None:
            self.cart_reference = reference
            self.name = self.cart_reference
            self.validation_statut = False
            self.products = {}
            self.cart = {}
            self.logistic = {}
            #self.load()
        else:
            self.reference_error(reference)

    def reference_error(self, reference):
        """Error while a a reference is uncorrect"""
        raise ValueError('Invalid reference %s' % str(reference))

    def add_product(self, reference=None, price=0.0, vat=0.0, quantity=1.0,
                    included_tax=True, weight=0):
        """Add the product into the cart"""
        if reference is not None:
            self._update = False
            if reference not in self.products:
                price = float(price)
                if included_tax:
                    price = Price(price, vat=vat)
                else:
                    price = Price(without_tax=price, vat=vat)

                self.products[reference] = {}
                self.products[reference]['price'] = price()
                self.products[reference]['weight'] = weight
                self.products[reference]['quantity'] = float(quantity)
            else:
                self.products[reference]['quantity'] += float(quantity)

            #self.save()
        else:
            self.reference_error(reference)

    def del_all_product(self, reference=None):
        """Delete a product into the cart"""
        if reference in self.products:
            self._update = False
            del self.products[reference]
            #self.save()

    def del_product(self, reference=None, quantity=1):
        """Delete a product into the cart"""
        if reference in self.products:
            self._update = False
            self.products[reference]['quantity'] -= quantity
            if self.products[reference]['quantity'] < 1:
                self.del_all_product(reference=reference)
            #self.save()

    def validation(self, flag=True):
        """Set the state of the caddy"""
        self.validation_statut = flag
        #self.save()

    def remove(self):
        """User method to delete the cart from the persistence"""
        self._update = False
        self.products = {}

    def add_reduction(self, value, percentage=False, ref=None, number=None):
        if ref is None:
            self._update = False
            reduction = {'value' : value,
                         'percentage' : percentage,
                         }
            if not 'reductions' in self.cart:
                self.cart['reductions'] = [reduction]
            else:
                self.cart['reductions'].append(reduction)

        else:
            if ref in self.products:
                self._update = False
                product = self.products[ref]
                reduction = {'value' : value,
                             'percentage' : percentage,
                             }
                if not 'reductions' in product:
                    product['reductions'] = [reduction]
                else:
                    product['reductions'].append(reduction)

    def set_quantity(self, reference, quantity=0):
        """Change the quantity of a product in the cart"""
        if reference in self.products:
            self._update = False
            if quantity == 0:
                self.del_all_product(reference)
            else:
                quantity = int(quantity)
                self.products[reference]['quantity'] = float(quantity)
                #self.save()
        else:
            self.reference_error(reference)

    def get_product_property(self, reference, property):
        """Return the quantity of a product"""
        if reference in self.products:
            return self.products[reference].get(property)
        else:
            self.reference_error(reference)

    def update(self):
        self.rules.amount_chain(self)
        self._update = True

    def get_cart_amount(self):
        """Return the amount of the caddy"""
        if not self._update:
            self.update()
        return round(self.cart['amount'], 2)

    def get_cart_detail_amount(self):
        if not self._update:
            self.update()
        return self.cart

    def update_country_shipping(self, iso):
        self._update = False
        self.logistic['country_iso'] = iso
