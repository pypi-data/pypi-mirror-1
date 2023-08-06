#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2006 Emencia
#
# Authors: Lafaye Philippe (RAGE2000) <lafaye@emencia.com>
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

"""This script load dynamically rules in fonction of conf files"""

from standard_rules import ObjectReduction, ObjectAmount, CartReduction, \
                           CartAmount

class RulesInit(object):
    """This class will load rules chain from the conf file and initializing
    it"""
    def __init__(self):
#        if conf.has_info('ecscart.connector'):
#            self.connector = conf.get('ecscart.connector')
#            rules_chains = conf.keys_section('ecscart_rules')
#
#            #now we will build rules chain
#            self.chain = {}
#            for chain_key in rules_chains:
#                process = None
#                chain_name = chain_key.split('.')[-1]
#                for rule_path in conf.get(chain_key).split(','):
#                    rule_path = rule_path.strip()
#                    # get the name of module and name of rule class
#                    module_name, rule_name = rule_path.split('.')
#                    # try to import the rule
#                    exec "from %s import %s as rule" % (module_name,
#                                                        rule_name)
#                    # chain the rule
#                    process = rule(process)
#                # the chain build is over, add it into the chain dict
#                self.chain[chain_name] = process
#        else:
        self.connector = 'standard'
        amount_chain = [CartReduction, CartAmount, ObjectReduction,
                        ObjectAmount]
        process = None
        for rule in amount_chain:
            process = rule(process)
        self.chain = {'amount': process}


    def amount_chain(self, cart):
        return self.chain['amount'](cart)


