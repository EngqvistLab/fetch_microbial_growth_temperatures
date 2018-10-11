#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to get the data shelves from the different databases and fuse them.
#
#copyright (C) 2017-2018  Martin Engqvist | martin.engqvist@chalmers.se
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#LICENSE:
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Library General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

import sys
if sys.version_info[0] != 2:
    sys.exit("Sorry, only Python 2 is supported by this script.")


import shelve
import os
from os.path import join, exists
import json

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external')
INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate')
FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')


#ATCC data
s = shelve.open(join(RAW_FOLDER, 'ATCC/ATCC_parsed_cleaned.db'))
all_data = s['data']
s.close()

#DSMZ data
s = shelve.open(join(RAW_FOLDER, 'DSMZ/DSM_parsed_cleaned.db'))
all_data.extend(s['data'])
s.close()

#NCTC data
s = shelve.open(join(RAW_FOLDER, 'NCTC/NCTC_parsed_cleaned.db'))
all_data.extend(s['data'])
s.close()

#Pasteur data
s = shelve.open(join(RAW_FOLDER, 'Pasteur/Pasteur_parsed_cleaned.db'))
all_data.extend(s['data'])
s.close()

#NIES data
s = shelve.open(join(RAW_FOLDER, 'NIES/NIES_parsed_cleaned.db'))
all_data.extend(s['data'])
s.close()

#BacDive data
s = shelve.open(join(RAW_FOLDER, 'BacDive/BacDive_parsed_cleaned.db'))
all_data.extend(s['data'])
s.close()




def merge_data():
    '''Collect all the information on one organism from all databases and store in shelve'''
    print('Merging data')
    #first find all unique organisms
    all_unique = set([])
    for record in all_data:
        if record['name'] != None:
            all_unique.add(record['name'].lower())

    out_data = {}
    for org in all_unique:
        out_data[org] = {}
        out_data[org]['temp'] = []
        out_data[org]['taxid'] = []
        out_data[org]['lineage'] = []
        out_data[org]['medium'] = []
        out_data[org]['db'] = []
        out_data[org]['domain'] = []
        out_data[org]['risk'] = []

    #for each shelve, poupulate
    for record in all_data:
        org = record['name'].lower()
        out_data[org]['temp'].append(record['temp'])
        out_data[org]['taxid'].append(record['taxid'])
        out_data[org]['lineage'].append(record['lineage'])
        out_data[org]['medium'].append(record['medium'])
        out_data[org]['db'].append(record['db'])
        out_data[org]['domain'].append(record['domain'])
        out_data[org]['risk'].append(record['risk'])

    s = shelve.open(join(FINAL_FOLDER, 'all_data.db'))
    s['data'] = out_data
    s.close()
    print('Done')




def output_temperature_flatfile():
    '''Make flatfile for temperatures in .tsv format as well as a json dump'''
    s = shelve.open(join(FINAL_FOLDER, 'all_data.db'))
    data = s['data']
    s.close()

    json_data = {}

    #make average of the temperatures
    for org in data.keys():
        if org == 'bacteriophage lambda':
            continue

        #skip nones
        temps = [float(s) for s in data[org]['temp'] if s is not None]

        #skip enpty dictionaries
        if temps == []:
            data[org]['temp'] = None
            continue

        #make average
        data[org]['temp'] = int(round( sum(temps)/float(len(temps)) ))

        #make sure there is only one kind of taxid for each organism
        if len(set(data[org]['taxid'])) == 1:
            data[org]['taxid'] = data[org]['taxid'][0]
        else:
            raise ValueError

        #domain
        if len(set(data[org]['domain'])) == 1:
            data[org]['domain'] = data[org]['domain'][0]
        else:
            raise ValueError

        #lineage text
        if all([data[org]['lineage'][0] == s for s in data[org]['lineage']]):
            data[org]['lineage'] = data[org]['lineage'][0]
        else:
            print(data[org]['lineage'])

        #lineage number
        data[org]['lineage_taxid'] = 'test'

    #write to json file
    with open(join(FINAL_FOLDER, 'temperature_data.xml'), 'w') as f:
        json.dump(data, f)

    with open(join(FINAL_FOLDER, 'temperature_data.tsv'), 'w') as f:
        f.write('organism\tdomain\ttemperature\ttaxid\tlineage_text\tsuperkingdom\tphylum\tclass\torder\tfamily\tgenus\n')
        for org in sorted(data.keys()):
            if org == 'bacteriophage lambda':
                continue

            temperature = data[org]['temp']
            if temperature is None:
                continue
            domain = data[org]['domain']
            taxid = data[org]['taxid']
            lineage_text = data[org]['lineage']['lineage_text']
            lineage_number = data[org]['lineage']['lineage_taxid']
            f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (org.replace('.', '').replace(' ', '_'), domain, temperature, taxid, lineage_text, lineage_number['superkingdom'], lineage_number['phylum'], lineage_number['class'], lineage_number['order'], lineage_number['family'], lineage_number['genus']))






merge_data()
output_temperature_flatfile()
