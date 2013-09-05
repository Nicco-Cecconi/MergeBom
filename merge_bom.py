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
# Copyright 2012 Daniele Basile <asterix24@gmail.com>
#
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys, os
import re

def fillRowCenter(row, s):
    r = row[:(len(row)/2) - (len(s)/2)] + s + row[(len(row)/2) + (len(s)/2):]
    if len(r) < len(row):
        r = r + row[-1] * (len(row) - len(r))
    if len(r) > len(row):
        r = r[:-1 * (len(r) - len(row))]
    return r

def fillTableRow(row, col1, col2, col3):
    col1 = "%s" % col1
    col2 = "%s" % col2
    col3 = "%s" % col3

    if len(col1) > 10:
        col1 = col1[:10]
    s = col1 + row[10 - len(col1):]

    WCOL2=40
    if len(col2) > WCOL2:
        col2 = col2[:WCOL2]
        print "trim col2"
    s = s[:(WCOL2-len(col2))] + col2 + s[WCOL2:]

    if len(col3) > (len(row) - WCOL2):
        col3 = col3[:len(row) - WCOL2]
        print "trim col3"

    s = s[: len(row) - len(col3)] + col3

    return s


QUANTITY=0
REF=1
COMMENT=2
FOOTPRINT=3
DESCRIPTION=4

if len(sys.argv) < 2:
    print sys.argv[0], " <csv file name1> <csv file name2> .."
    exit (1)

in_delimiter = ','
if '-isc' in sys.argv:
    sys.argv.remove('-isc')
    in_delimiter = ';'

out_delimiter = ','
if '-osc' in sys.argv:
    sys.argv.remove('-osc')
    out_delimiter = ','

table = []
CSV_NUM = len(sys.argv[1:])
QUANTITY = CSV_NUM + QUANTITY
REF = CSV_NUM + REF
COMMENT_PLUS = CSV_NUM + COMMENT
DESCRIPTION_PLUS= CSV_NUM + DESCRIPTION
FOOTPRINT_PLUS= CSV_NUM + FOOTPRINT

header = []
table_dict = {}
pre_col = [0] * CSV_NUM
index = 0
key = ''

for i in sys.argv[1:]:
    csv_table = csv.reader(open(i, 'rb'), delimiter=in_delimiter)
    for j in csv_table:
        #Check bom format
        if (j == []):
            continue
        if (j[0] == 'Quantity'):
            header = j
            header = sys.argv[1:] + header
            continue

        try:
            if (j[REF - CSV_NUM][0].lower() == 'j') or ('LED' in j[DESCRIPTION].upper()) or ('TACTILE' in j[DESCRIPTION].upper()):
                key = j[FOOTPRINT] + j[DESCRIPTION]
                print "Except: > ",key
            else:
                key = j[COMMENT] + j[FOOTPRINT] + j[DESCRIPTION]
        except IndexError:
            print "INDEX ERROR"
            print j
            print "..........."
            continue

        if key == '':
            print "NULL KEY ERROR"
            print j
            print "..........."
            continue


        if key in table_dict:
            table_dict[key][QUANTITY] += int(j[QUANTITY - CSV_NUM])
            table_dict[key][REF] += ", " + j[REF - CSV_NUM]

            if (j[REF - CSV_NUM][0].lower() == 'j') or ('LED' in j[DESCRIPTION].upper()) or ('TACTILE' in j[DESCRIPTION].upper()):
                table_dict[key][COMMENT_PLUS] += ", " + j[COMMENT]
                table_dict[key][index] += int(j[QUANTITY - CSV_NUM])
            else:
                table_dict[key][index] = j[QUANTITY - CSV_NUM]
        else:
            try:
                table_dict[key] = pre_col + j
                table_dict[key][QUANTITY] = int(table_dict[key][QUANTITY])
                table_dict[key][index] = int(j[QUANTITY - CSV_NUM])
            except ValueError:
                print "FIRST COL NOT INT ERROR"
                print j
                print "..........."
                continue

            if (j[REF - CSV_NUM][0].lower() == 'j') or ('LED' in j[DESCRIPTION].upper()) or ('TACTILE' in j[DESCRIPTION].upper()):
                table_dict[key][COMMENT_PLUS] = j[COMMENT]

    index += 1


d = {}
l = sorted(table_dict.values(), key=lambda ref: ref[REF][:2])
for g in l:
    c = re.search('^[a-zA-Z_]{1,3}', g[REF])
    key = c.group().upper()

    # Buttons and spacer
    if key in ['B', 'BT', 'SCR', 'SPA', 'BAT','SW']:
        key = 'S'
    # Fuses
    if key in ['G']:
        key = 'F'
    # Tranformer
    if key in ['T' ]:
        key = 'TR'
    # Resistors, array, etc.
    if key in ['RN', 'R_G']:
        key = 'R'
    # Discarted ref
    if key in ['TP']:
        print "WARNING WE SKIP THIS KEY"
        print 'key [%s]' % key
        print '.........'
        continue

    if d.has_key(key):
        d[key].append(g)
    else:
        d[key] = [g]

    print 'Group Key:',c.group(), g[REF]

SEPARATOR_NUM = len(l[0]) - 1
ORDER_PATTERN = ['J', 'S', 'F','R','C','D','DZ','L', 'Q','TR','Y', 'U']
ORDER_PATTERN_NAMES = {
    'J':['* J Connectors *'],
    'S':['* S Mechanical parts and buttons *'],
    'F':['* F Fuses *'],
    'R':['* R Resistors *'],
    'C':['* C Capacitors *'],
    'D':['* D Diodes *'],
    'DZ':['* DZ Zener, Schottky, Transil *'],
    'L': ['* L Inductors, chokes *'],
    'Q': ['* Q Transistors *'],
    'TR':['* TR Transformers *'],
    'Y': ['* Y Cristal, quarz, oscillators*'],
    'U': ['* U IC *']
}
#Add separator from each group of components.
for i in ORDER_PATTERN_NAMES.keys():
    ORDER_PATTERN_NAMES[i] = (([''] * REF) + ORDER_PATTERN_NAMES[i] + ([''] * (SEPARATOR_NUM - REF)))
    print ORDER_PATTERN_NAMES[i]


for k in d.keys():
    if k in ['D', 'J', 'S', 'U']:
        d[k] = sorted(d[k], key=lambda ref: ref[DESCRIPTION_PLUS])
    else:
        d[k] = sorted(d[k], key=lambda ref: ref[COMMENT_PLUS])

#Check missing group code.
for j in d.keys():
    if j not in ORDER_PATTERN:
        print 'Missing order pattern key: \"%s\"' % j
        print 'In BOM:', d.keys()
        print 'In mergebom:', ORDER_PATTERN
        sys.exit(0)

with open('merged_bom.csv', 'wb') as csvfile:
    data = csv.writer(csvfile, delimiter=out_delimiter)
    data.writerow(header)
    for p in ORDER_PATTERN:
        if d.has_key(p):
            data.writerow(ORDER_PATTERN_NAMES[p])
            for i in d[p]:
                data.writerow(i)

print
print
print "=" * 10, "MERGE STATISTICS", "=" *10
print
print

total = 0
recap = {}
for p in ORDER_PATTERN:
    if d.has_key(p):

        """
        implementare le funzioni per l'ordinamento dei
        valori delle resistenze e delle capacita'
        if p == 'R':
            print d[p]
            def __sortDict(d):
               d = d.get(order_by_field, None)
               if order_by_field in cfg.DB_DATA_FIELD:
                   if d is None:
                       return datetime.date(2000,1,1)
                   return d
               return sorted(data, key=__sortDict, reverse=ordering)
        """


        s = ORDER_PATTERN_NAMES[p][2]
        s = s.replace('*','')
        print
        print fillRowCenter("*" * 80, s)
        recap[s] = 0
        for i in d[p]:
            if i[QUANTITY] != '':
                total += i[QUANTITY]
                recap[s] += i[QUANTITY]
                print fillTableRow(" " * 80, "n.%d" % i[QUANTITY], i[COMMENT_PLUS], i[FOOTPRINT_PLUS])
                #print "n.%3d %20s %30s" % (


print
print
print "~" * 10, "Total", "~" *10
for r in recap.keys():
    print "%4d: %s" % (recap[r], r)

print "-" * 24
print "%4d Total components" % total
print "~" * 24
print
print

