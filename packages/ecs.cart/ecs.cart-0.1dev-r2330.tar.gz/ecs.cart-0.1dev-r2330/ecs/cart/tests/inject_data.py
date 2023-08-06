#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2006 Emencia
#
#
# Authors: Tarek Ziadé <tarek@emencia.com>
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
# $Id: test_docs.py 1048 2007-02-05 17:22:50Z rage $

from emencia.ecsdb import getMapping

def delete_logistic_tables():
    vat = getMapping('vat')
    vatvalue = getMapping('vatvalue')
    geozone = getMapping('geographicalzone')
    country = getMapping('country')
    deliveryprice = getMapping('deliveryprice')
    vatvalue.delete()
    vat.delete()
    geozone.delete()
    country.delete()
    deliveryprice.delete()

def inject_test_logistic_data():
    fake_vat = ((1,'high_vat'),(2,'low_vat'))
    vat = getMapping('vat')
    if vat.select().fetchall() == []:
        for id, label in fake_vat:
            vat.insertLine(id=id, label_label_msgid=label)
    fake_zone = (('A', None, False, None, False, None, 1),
                ('B', 10, True, 600, True, 2, 1))
    geozone = getMapping('geographicalzone')
    if geozone.select().fetchall() == []:
        for iso, additional_fee, freeport_activated, freeport,\
            delivery_tax_activated, delivery_tax, delivery_vat_vat_id in\
            fake_zone:
            geozone.insertLine(iso=iso, additional_fee=additional_fee,
                               freeport_activated=freeport_activated,
                               freeport=freeport,
                               delivery_tax_activated=delivery_tax_activated,
                               delivery_tax=delivery_tax,
                               delivery_vat_vat_id=delivery_vat_vat_id)
    fake_country = (('FR', None, True, 500, False, None, 1, 'A'),
                    ('GB', 5, False, None, True, 2, 1, 'A'),
                    ('AU', None, None, None, False, None, 2, 'B'),
                   )
    country = getMapping('country')
    if country.select().fetchall() == []:
        for iso, additional_fee, freeport_activated, freeport,\
            delivery_tax_activated, delivery_tax, delivery_vat_vat_id,\
            geographicalzone_geographicalzone_iso in fake_country:
            country.insertLine(iso=iso, additional_fee=additional_fee,
                               freeport_activated=freeport_activated,
                               freeport=freeport,
                               delivery_tax_activated=delivery_tax_activated,
                               delivery_tax=delivery_tax,
                               delivery_vat_vat_id=delivery_vat_vat_id,
                               geographicalzone_geographicalzone_iso= \
                               geographicalzone_geographicalzone_iso)

    fake_vatvalue = ((1, 'FR', 5.5),
                      (2, 'FR', 19.6),
                      (1, 'GB', 5),
                      (2, 'GB', 10),
                      (1, 'AU', 2),
                      (2, 'AU', 12),
                     )
    vatvalue = getMapping('vatvalue')
    if vatvalue.select().fetchall() == []:
        for vat_vat_id, geographicalzone_geographicalzone_iso, value in\
            fake_vatvalue:
            vatvalue.insertLine(vat_vat_id=vat_vat_id,
                                geographicalzone_geographicalzone_iso=\
                                geographicalzone_geographicalzone_iso,
                                value=value)
    fake_delivertprice = ((1, 'A', 1, 'label_deliverypriceA1', 0, 1000, 12,
                           'label_deliverytimeA1', 10),
                          (2, 'A', 1, 'label_deliverypriceiA2', 1000, 100000, 12,
                           'label_deliverytimeA1', 12),
                          (3, 'B', 1, 'label_deliverypriceB1', 0, 1000, 20,
                           'label_deliverytimeA1', 8),
                          (4, 'B', 1, 'label_deliverypriceB2', 1000, 100000, 20,
                           'label_deliverytimeA1', 9),
                          (5, 'FR', 1, 'label_deliverypriceFR5', 0, 1000, 4,
                           'label_deliverytimeA1', 4),
                          (6, 'FR', 1, 'label_deliverypriceFR6', 1000, 100000, 4,
                           'label_deliverytimeA1', 6),
                         )

    deliveryprice = getMapping('deliveryprice')
    if deliveryprice.select().fetchall() == []:
        for (id, geographicalzone_geographicalzone_iso, deliver_deliver_id,
        label_label_msgid, weight_min, weight_max, time, time_label_msgid,
        amount) in fake_delivertprice:
            deliveryprice.insertLine(id=id,
                                     geographicalzone_geographicalzone_iso=\
                                     geographicalzone_geographicalzone_iso,
                                     deliver_deliver_id=deliver_deliver_id,
                                     label_label_msgid=label_label_msgid,
                                     weight_min=weight_min,
                                     weight_max=weight_max, time=time,
                                     time_label_msgid=time_label_msgid,
                                     amount=amount)
def delete_user_tables():
    user_address = getMapping('user_address')
    user_address.delete()
    ecsuser = getMapping('ecsuser')
    ecsuser.delete()
    address = getMapping('address')
    address.delete()


def inject_test_user_data():
    ecsuser = getMapping('ecsuser')
    if ecsuser.select().fetchall() == []:
        ecsuser.insertLine(id=1, login='test_user')

    fake_address = ((1, 'FR', True),
                    (2, 'GB', False),
                    (3, 'AU', False),
                   )
    address = getMapping('address')
    if address.select().fetchall() == []:
        for id, geographicalzone_geographicalzone_iso, is_user in\
            fake_address:
            address.insertLine(id=id,
                               geographicalzone_geographicalzone_iso=\
                               geographicalzone_geographicalzone_iso,
                               is_user=is_user)
    user_address = getMapping('user_address')
    if user_address.select().fetchall() == []:
        for address_address_id in xrange(1,4):
            user_address.insertLine(user_ecsuser_id=1,
                                    address_address_id=address_address_id)

def delete_product_tables():
    productprice = getMapping('productprice')
    productprice.delete()
    product = getMapping('product')
    product.delete()


def inject_test_product_data():
    product = getMapping('product')
    fake_product = ((1, 'coca', 1, 50),
                    (2, 'shoes', 2, 100),
                    (3, 'television', 2, 10000),
                   )
    if product.select().fetchall() == []:
        for id, reference, vat_idvat, weight in fake_product:
            product.insertLine(id=id, reference=reference,
                               vat_idvat=vat_idvat, weight=weight)

    productprice = getMapping('productprice')
    fake_price = ((1, 1, 2, 0, 2),
                  (2, 1, 1.5, 2, 3),
                  (3, 2, 15, 0, 9999),
                  (4, 3, 350, 0, 9999),
                 )
    if productprice.select().fetchall() == []:
        for id, product_product_id, price, quantity_min, quantity_max in\
            fake_price:
            productprice.insertLine(id=id,
                                    product_product_id=product_product_id,
                                    price=price, quantity_min=quantity_min,
                                    quantity_max=quantity_max)



def delete_tables():
    delete_logistic_tables()
    delete_user_tables()
    delete_product_tables()

def inject_test_data():
    delete_tables()
    inject_test_logistic_data()
    inject_test_user_data()
    inject_test_product_data()


def inject_xtox_relation():
    inject_test_data()
    category_relation = getMapping('category_relation')
    category_relation.insertLine(child_category_id=2, parent_category_id=2,
                                 structure_structure_id=1)

def inject_circle_relation():
    inject_test_data()
    category_relation = getMapping('category_relation')
    category_relation.insertLine(child_category_id=1, parent_category_id=2,
                                 structure_structure_id=1)
    category_relation.insertLine(child_category_id=9, parent_category_id=10,
                                 structure_structure_id=1)

