#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#this script goes through a ATCC lists of organisms and downloads these as html files.
#it gives a snapshot of their database such that I can download info for the individual organisms after
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


import urllib2
import os
from os.path import join, exists
import time

PROJ_ROOT_DIRECTORY = '.'
ATCC_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/ATCC')
ATCC_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/ATCC')
ATCC_FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final/ATCC')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')

#make folder if it does not exist
if not exists(TAX_FOLDER):
	os.makedirs(TAX_FOLDER)

if not exists(ATCC_RAW_FOLDER):
	os.makedirs(ATCC_RAW_FOLDER)

if not exists(ATCC_INTERMEDIATE_FOLDER):
	os.makedirs(ATCC_INTERMEDIATE_FOLDER)

if not exists(ATCC_FINAL_FOLDER):
	os.makedirs(ATCC_FINAL_FOLDER)

if not exists(join(ATCC_RAW_FOLDER, 'Lists_of_all')):
    os.makedirs(join(ATCC_RAW_FOLDER, 'Lists_of_all'))

if not exists(join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Fung_Yeast')):
    os.makedirs(join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Fung_Yeast'))

if not exists(join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Bac_Phage')):
    os.makedirs(join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Bac_Phage'))

if not exists(join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Prot_Alg')):
    os.makedirs(join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Prot_Alg'))



def get_url(url_link, typeof):
    print(url_link)
    #write to file
    target_file = url_link.split('/')[-1].replace('?', '_').replace(':', '_').replace('=', '_').replace(',', '_').replace('.', '_')
    if typeof == 'protalg':
        filepath = join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Prot_Alg', target_file)
        if exists(filepath) is False:
            html_file = urllib2.urlopen(url_link).read()
            with open(filepath, 'w') as f:
                f.write(html_file)
            time.sleep(1)

    elif typeof == 'fungyeast':
        filepath = join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Fung_Yeast', target_file)
        if exists(filepath) is False:
            html_file = urllib2.urlopen(url_link).read()
            with open(filepath, 'w') as f:
                f.write(html_file)
            time.sleep(1)

    elif typeof == 'bacphage':
        filepath = join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Bac_Phage', target_file)
        if exists(filepath) is False:
            html_file = urllib2.urlopen(url_link).read()
            with open(filepath, 'w') as f:
                f.write(html_file)
            time.sleep(1)

    else:
        raise ValueError





#bac_phage, 18335 total
for i in range(0, 18400, 100):
    url = 'https://www.lgcstandards-atcc.org/Products/Cells_and_Microorganisms/Bacteria/Alphanumeric_Genus__Species.aspx?dsNav=Rpp:100,Ro:%s' % i
    get_url(url, 'bacphage')

#fungi and yeast, 58183 total
for i in range(0, 58200, 100):
    url = 'https://www.lgcstandards-atcc.org/Products/Cells_and_Microorganisms/Fungi_and_Yeast/Fungi_and_Yeast_Alphanumeric.aspx?dsNav=Rpp:100,Ro:%s' % i
    get_url(url, 'fungyeast')


#protozoa, 2430 total (together with algae)
for i in range(0, 2500, 100):
    url = 'https://www.lgcstandards-atcc.org/Products/Cells_and_Microorganisms/Protozoa/Protozoa_Alphanumeric.aspx?dsNav=Rpp:100,Ro:%s' % i
    get_url(url, 'protalg')

#algae, 2430 total (together with protozoa)
for i in range(0, 2500, 100):
    url = 'https://www.lgcstandards-atcc.org/Products/Cells_and_Microorganisms/Protozoa/Algae_Alphanumeric.aspx?dsNav=Rpp:100,Ro:%s' % i
    get_url(url, 'protalg')
