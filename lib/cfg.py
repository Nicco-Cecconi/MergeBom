#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MergeBom is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Copyright 2017 Daniele Basile <asterix24@gmail.com>
#

"""
MergeBOM Default configuration
"""


import sys
import ConfigParser
import toml
import lib

MERGEBOM_VER = "1.0.0"

LOGO_SIMPLE = """

#     #                             ######
##   ## ###### #####   ####  ###### #     #  ####  #    #
# # # # #      #    # #    # #      #     # #    # ##  ##
#  #  # #####  #    # #      #####  ######  #    # # ## #
#     # #      #####  #  ### #      #     # #    # #    #
#     # #      #   #  #    # #      #     # #    # #    #
#     # ###### #    #  ####  ###### ######   ####  #    #

"""

LOGO = """

███╗   ███╗███████╗██████╗  ██████╗ ███████╗██████╗  ██████╗ ███╗   ███╗
████╗ ████║██╔════╝██╔══██╗██╔════╝ ██╔════╝██╔══██╗██╔═══██╗████╗ ████║
██╔████╔██║█████╗  ██████╔╝██║  ███╗█████╗  ██████╔╝██║   ██║██╔████╔██║
██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██╔══██╗██║   ██║██║╚██╔╝██║
██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝███████╗██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝

"""

ENG_LETTER = {
    'G': (1e9, 1e8),
    'M': (1e6, 1e5),
    'k': (1e3, 1e2),
    'R': (1, 0.1),
    'u': (1e-6, 1e-7),
    'n': (1e-9, 1e-10),
    'p': (1e-12, 1e-13),
}

CATEGORY_TO_UNIT = {
    'R': "ohm",
    'C': "F",
    'L': "H",
    'Y': "Hz",
}

VALID_KEYS = [
    u'designator',
    u'comment',
    u'footprint',
    u'description',
    u'farnell',
]

EXTRA_KEYS = [
    u'date',
    u'project',
    u'hardware_version',
    u'pcb_version',
]

CATEGORY_NAMES_DEFAULT = [
    {
        'name': 'Connectors',
        'desc': 'Connectors and holders',
        'group': ['X', 'P', 'SIM'],
        'ref': 'J',
    },
    {
        'name': 'Mechanicals',
        'desc': 'Mechanical parts and buttons',
        'group': [
            'SCR',
            'SPA',
            # Battery
            'BAT',
            # Buzzer
            'BUZ',
            # Buttons
            'BT',
            'B',
            'SW',
            'K'],
        'ref': 'S',
    },
    {
        'name': 'Fuses',
        'desc': 'Fuses discrete components',
        'group': ['g'],
        'ref': 'F',
    },
    {
        'name': 'Resistors',
        'desc': 'Resistor components',
        'group': ['RN', 'R_G'],
        'ref': 'R',
    },
    {
        'name': 'Capacitors',
        'desc': 'Capacitors',
        'group': [],
        'ref': 'C',
    },
    {
        'name': 'Diode',
        'desc': 'Diodes, Zener, Schottky, LED, Transil',
        'group': ['DZ'],
        'ref': 'D',
    },
    {
        'name': 'Inductors',
        'desc': 'L  Inductors, chokes',
        'group': [],
        'ref': 'L',
    },
    {
        'name': 'Transistor',
        'desc': 'Q Transistors, MOSFET',
        'group': [],
        'ref': 'Q',
    },
    {
        'name': 'Transformes',
        'desc': 'TR Transformers',
        'group': ['T'],
        'ref': 'TR',
    },
    {
        'name': 'Cristal',
        'desc': 'Cristal, quarz, oscillator',
        'group': [],
        'ref': 'Y',
    },
    {
        'name': 'IC',
        'desc': 'Integrates and chips',
        'group': [],
        'ref': 'U',
    },
    {
        'name': 'DISCARD',
        'desc': 'Reference to discard, to not put in BOM',
        'group': ['TP'],
        'ref': '',
    },
]


NOT_POPULATE_KEY = ["NP", "NM"]
NP_REGEXP = r"^NP\s"


class CfgMergeBom(object):
    """
    MergeBOM Configuration
    """

    def __init__(self, cfgfile_name=None, handler=sys.stdout, terminal=True):
        self.handler = handler
        self.terminal = terminal
        self.category_names = CATEGORY_NAMES_DEFAULT

        if cfgfile_name is not None:
            try:
                config_file = open(cfgfile_name)
                config = toml.loads(config_file.read())
                self.category_names = config.get('category_names', None)
            except IOError as e:
                lib.error("Configuration: %s" % e,
                              self.handler, terminal=self.terminal)
                lib.warning("No Valid Configuration file! Use Default",
                                self.handler, terminal=self.terminal)

        if self.category_names is None:
            lib.warning("No Valid Configuration file! Use Default",
                            self.handler, terminal=self.terminal)


    def check_category(self, group_key):
        if not group_key:
            return group_key

        for item in self.category_names:
            if group_key in item['group'] or group_key == item['ref']:
                return item['ref']

        return None

    def categories(self):
        categories = []
        for item in self.category_names:
            if item['ref']:
                categories.append(item['ref'])

        return categories

    def get(self, category, key):
        """
        By category and key get all related info
        """
        for item in self.category_names:
            if item['ref'] == category:
                return item[key]

        return None


def cfg_version(filename):
    """
    Get all field from version file, and put it in a dictionary of dictionary.
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(filename))

    cfg = {}
    for section in config.sections():
        d = {}
        d['name'] = config.get(section, 'name')
        d['hw_ver'] = config.get(section, 'hw_ver')
        d['pcb_ver'] = config.get(section, 'pcb_ver')
        d['date'] = config.get(section, 'date')
        cfg[section] = d
    return cfg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage %s <cfg filename>" % sys.argv[0]
        sys.exit(1)

    config = "Vuoto"
    with open(sys.argv[1]) as configfile:
        config = toml.loads(configfile.read())

    print type(config), len(config)
    print config.keys()
    print config['category_names']
