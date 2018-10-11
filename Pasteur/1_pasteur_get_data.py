#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to download growth temperatures from the Pasteur resource.
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


import string
import shelve
import os
import re
from os.path import join, exists

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
Pasteur_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/Pasteur')
Pasteur_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/Pasteur')
Pasteur_FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final/Pasteur')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')

#make folder if it does not exist
if not exists(TAX_FOLDER):
	os.makedirs(TAX_FOLDER)

if not exists(Pasteur_RAW_FOLDER):
	os.makedirs(Pasteur_RAW_FOLDER)

if not exists(Pasteur_INTERMEDIATE_FOLDER):
	os.makedirs(Pasteur_INTERMEDIATE_FOLDER)

if not exists(Pasteur_FINAL_FOLDER):
	os.makedirs(Pasteur_FINAL_FOLDER)




def clean_name(dirty_name):
    '''Clean bacterial name from contaminating characters.'''
    if len(dirty_name.split(' ')) == 1:
        name = dirty_name + ' sp.'
    else:
        name = dirty_name.split(' ')[0] + ' ' + dirty_name.split(' ')[1]

    squeaky_clean = name.replace("'", "").replace('"', '').replace(';', '').replace(':', '')

    #make sure name is ok
    if not all([s in list(string.ascii_lowercase + string.ascii_uppercase + ' .') for s in squeaky_clean]):
        #print(squeaky_clean)
        return None

    return squeaky_clean


def get_exel_exported_data():
    '''
    Opens the file I got from Pasteur, parses it and stores at a python shelve.
    '''
    print('Parsing Pasteur')
    sh = shelve.open(join(Pasteur_INTERMEDIATE_FOLDER, 'Pasteur_parsed.db'))
    data_list = [] # to hold the data
    for data_file in ['Collections_Pasteur.tsv', 'Collections_Pasteur_cyano.tsv']:
        with open(join(Pasteur_RAW_FOLDER, data_file), 'r') as f:
            f.readline()

            for line in f:
                temp = line.split('\t')


                db = 'CIP'
                strain_id = temp[1].split()[-1]
                name = temp[2].strip().replace('  ', ' ').lower()
                synonyms = [s.strip().replace('  ', ' ').lower() for s in temp[8].split(',') if s.strip().replace('  ', ' ').lower() != '']
                all_names = set([name] + synonyms)
                domain = None
                temperature = None
                risk = None
                isolation = None
                medium = None
                taxid = None


                #get the domain
                if temp[3].decode('utf-8').replace(u'\xe9', u'e').encode('utf-8') in ['Bacteries', 'Cyanobacteries']:
                    domain = 'bacteria'

                #get growth temperature
                t_initial = temp[11].decode('utf-8').replace(u'\xb0', u'').encode('utf-8')
                if t_initial != '':
                    temperature = float(t_initial.replace('C', '').replace('c', ''))

                    #remove those that are 0
                    if temperature == 0:
                        temperature = None

                #get the risk category
                risk = temp[-3]

                #get isolation place
                if temp[21].strip() != '':
                    isolation = temp[21].strip()

                #get growth medium
                if temp[-1].strip() != '':
                    medium = temp[-1].strip()

                #add one entry for each stran name (including synonyms)
                for current_name in all_names:
                    current_name = clean_name(current_name)

                    data = {}
                    data['db'] = db
                    data['id'] = strain_id
                    data['name'] = current_name
                    data['type'] = domain
                    data['temp'] = temperature
                    data['risk'] = risk
                    data['isolation'] = isolation
                    data['medium']  = medium
                    data['taxid'] = taxid
                    data_list.append(data)

    #shelve file
    sh['data'] = data_list
    sh.close()
    print('Done')


get_exel_exported_data()
