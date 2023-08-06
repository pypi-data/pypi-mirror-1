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

from ConfigParser import SafeConfigParser

from standard_rules import ObjectReduction, ObjectAmount, CartReduction, \
                           CartAmount

class RulesInit(object):
    """This class will load rules chain from the conf file and initializing
    it"""
    def __init__(self, conf_file=None):
        if conf_file is not None:
            if not os.path.exists(conf_file):
                raise IOError('%s does not exists' % path)
            confparser = SafeConfigParser()
            confparser.read(conf_file)
            self.connector = confparser.get('main', 'connector')
            rules_chains = confparser.items('rules')

            #now we will build rules chain
            from paste.util.import_string import simple_import
            self.chain = {}
            for chain_name, chain in rules_chains:
                chain = chain.replace('\n', ' ')
                process = None
                for module in chain.split(' '):
                    rule = simple_import(module)
                    # chain the rule
                    process = rule(process)
                # the chain build is over, add it into the chain dict
                self.chain[chain_name] = process
        else:
            self.connector = 'standard'
            amount_chain = [CartReduction, CartAmount, ObjectReduction,
                            ObjectAmount]
            process = None
            for rule in amount_chain:
                process = rule(process)
            self.chain = {'amount': process}


    def amount_chain(self, cart):
        return self.chain['amount'](cart)


