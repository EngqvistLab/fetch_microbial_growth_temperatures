#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to run the data fetching and parsing scripts for all six databases
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

import os
from os.path import join, exists
import shelve
import zipfile
from urllib2 import urlopen, URLError, HTTPError

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
DATA_BASE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external')
RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external')
INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate')
FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')



def download_taxonomy():
    '''
    Download NCBI taxonomy data
    '''
    mycmd = 'wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump_readme.txt -P ./data/raw_external/taxonomy_data --no-clobber'
    os.system(mycmd)

    mycmd = 'wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdmp.zip -P ./data/raw_external/taxonomy_data --no-clobber'
    os.system(mycmd)
        


def parse_all():
    #run ATCC
    mycmd = "python2 ATCC/1_make_strain_lists.py"
    os.system(mycmd)

    mycmd = "python2 ATCC/2_parse_strain_lists.py"
    os.system(mycmd)

    mycmd = "python2 ATCC/3_get_single_entries.py"
    os.system(mycmd)

    mycmd = "python2 ATCC/4_parse_single_entries.py"
    os.system(mycmd)


    #run BacDive
    mycmd = "python2 BacDive/1_BacDive_get_data.py"
    os.system(mycmd)


    #run DSMZ
    mycmd = "python2 DSMZ/1_DSM_get_data.py"
    os.system(mycmd)


    #run NCTC
    mycmd = "python2 NCTC/1_NCTC_get_data.py"
    os.system(mycmd)


    #run NIES
    mycmd = "python2 NIES/1_get_database.sh"
    os.system(mycmd)

    mycmd = "python2 NIES/2_NIES_get_data.py"
    os.system(mycmd)


    #run Pasteur
    mycmd = "python2 Pasteur/1_pasteur_get_data.py"
    os.system(mycmd)



def match_names():
    '''
    match names with taxonomy and write to shelves
    '''
    print('Matching names to TaxId')
    #ATCC data
    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'ATCC/ATCC_parsed.db'))
    atcc = sh['data']
    sh.close()

    #DSMZ data
    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'DSMZ/DSM_parsed.db'))
    dsmz = sh['data']
    sh.close()

    #NCTC data
    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'NCTC/NCTC_parsed.db'))
    nctc = sh['data']
    sh.close()

    #Pasteur data
    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'Pasteur/Pasteur_parsed.db'))
    pasteur = sh['data']
    sh.close()

    #NIES data
    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'NIES/NIES_parsed.db'))
    nies = sh['data']
    sh.close()

    #BacDive data
    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'BacDive/BacDive_parsed.db'))
    bacdive = sh['data']
    sh.close()

    data = [atcc, dsmz, nctc, pasteur, nies, bacdive]


    #make a listt of unique organism names in my data shelves
    unique_orgs = set([])
    for db in data:
        for item in db:
            if item['name'] is None:
                continue
            unique_orgs.add(item['name'].lower())

    #make a dictionary with each of these organism, use for matching to taxid
    unique_org_dict = {key:None for key in list(unique_orgs)}
    print(len(unique_org_dict.keys()))

    #open taxid file and find the taxid for each of the unique organisms
    lines_done = 0
    with zipfile.ZipFile(join(RAW_FOLDER, 'taxonomy_data', 'taxdmp.zip'), 'r') as myzip:

        #unpack name file
        with myzip.open('names.dmp', 'r') as f:

            #match each line against info inside my shelves
            for line in f:
                lines_done += 1
                #if lines_done % 10000 == 0:
                #    print(lines_done)

                #go through each line and get info
                parts = line.split('\t')
                taxid = parts[0]
                name = parts[2].lower()
                typeof = parts[6]

                if typeof not in ['scientific name', 'equivalent name', 'synonym']:
                    continue

                #for every tax id and name, match against my unique organisms
                if name in unique_orgs:
                    unique_org_dict[name] = taxid

    #now go through the shelves and assign the already matched taxids
    counter = 0
    matched = 0
    for db in data:
        for item in db:
            counter += 1
            orgname = item['name']

            #add taxid to shelve if name matches
            if orgname is not None:
                #print('yes', name, taxid)
                item['taxid'] = unique_org_dict[orgname.lower()]
                matched += 1

    print('Total', counter)
    print('Matched', matched)

    #save to shelves
    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'ATCC/ATCC_parsed_taxid.db'))
    sh['data'] = atcc
    sh.close()

    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'DSMZ/DSM_parsed_taxid.db'))
    sh['data'] = dsmz
    sh.close()

    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'NCTC/NCTC_parsed_taxid.db'))
    sh['data'] = nctc
    sh.close()

    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'Pasteur/Pasteur_parsed_taxid.db'))
    sh['data'] = pasteur
    sh.close()

    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'NIES/NIES_parsed_taxid.db'))
    sh['data'] = nies
    sh.close()

    sh = shelve.open(join(INTERMEDIATE_FOLDER, 'BacDive/BacDive_parsed_taxid.db'))
    sh['data'] = bacdive
    sh.close()

    print('Done')


download_taxonomy()
parse_all()
match_names() #match names with taxonomy and write to shelves
