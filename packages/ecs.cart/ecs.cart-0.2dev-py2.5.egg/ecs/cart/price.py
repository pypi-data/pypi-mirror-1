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

"""price module"""

class Price(object):
    """object for manipulate vat and reduction on price"""

    _without_tax = None
    _included_tax = None
    _amount_vat = None

    def __init__(self, included_tax=None, without_tax=None, vat=0.0):
        self._vat = vat
        if included_tax is None and without_tax is None:
            raise ValueError(('Need a included tax price or a without tax'
                              ' price'))
        elif included_tax is None:
            self.without_tax = float(without_tax)
        else:
            self.included_tax = float(included_tax)

    def __call__(self):
        return {'included_tax' : self.included_tax,
                'without_tax' : self.without_tax,
                'amount_vat' : self.amount_vat,
                'vat' : self.vat,
               }

    def build_included_tax(self):
        if self._without_tax is None:
            raise ValueError('Without tax is None')
        amount_vat = self.vat * self._without_tax / 100
        self._amount_vat = amount_vat
        self._included_tax = self._without_tax + self.amount_vat


    def build_without_tax(self):
        if self._included_tax is None:
            raise ValueError('Included tax is None')
        without_tax = self._included_tax / (1 + self.vat / 100)
        self._without_tax = without_tax
        self._amount_vat = self._included_tax - self._without_tax

    def _set_without_tax(self, without_tax):
        self._without_tax = without_tax
        self.build_included_tax()

    def _set_included_tax(self, included_tax):
        self._included_tax = included_tax
        self.build_without_tax()

    def _set_vat(self, vat):
        error_message = "It's forbidden to set directly the vat attribute"
        raise AttributeError(error_message)

    def _set_amount_vat(self, amount_vat):
        error_message = "It's forbidden to set directly the vat_amount "\
                        "attribute"
        raise AttributeError(error_message)

    def _get_without_tax(self): return self._without_tax

    def _get_included_tax(self): return self._included_tax

    def _get_vat(self): return self._vat

    def _get_amount_vat(self):
        return self._amount_vat

    without_tax = property(_get_without_tax, _set_without_tax)

    included_tax = property(_get_included_tax, _set_included_tax)

    vat = property(_get_vat, _set_vat)

    amount_vat = property(_get_amount_vat, _set_amount_vat)
