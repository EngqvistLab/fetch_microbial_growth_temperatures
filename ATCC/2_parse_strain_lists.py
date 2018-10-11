#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#this script goes through the lists I downloaded from ATCC and gets all the ATCC numbers and their url.
#these are stored in a persistent shelve and will be used to individually query each one for name and growth  temperature
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


import re
import shelve
import os
from os.path import join, exists

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


#make regular expression for replacing html tags
pattern = re.compile(r'''ATCC<sup>&reg;</sup>(.*?)<sup>&trade;</sup>	#anything between ATCC<sup>&reg;</sup> and <sup>&trade;</sup>
						''', re.VERBOSE)

def parse_bac_phage():
    #parses bacteria and phages, there should be 18335 total
    master_list = []
    target_dir = join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Bac_Phage')
    for fi in os.listdir(target_dir):

		#get file data
		file_path =	join(target_dir, fi)
		with open(file_path, 'r') as f:
			html_file = f.read()

		#get the ATCC numbers and make sure there's 100 of them
		m =  pattern.findall(html_file)
		if len(m) != 100:
			print('File %s contains %s entries and not 100' % (fi, len(m)))

		#remove whitespace and add to master list
		m = [s.replace(' ', '') for s in m]
		master_list.extend(m)

    #save list as a shelf
    s = shelve.open(join(ATCC_RAW_FOLDER, 'ATCC_master.db'), writeback=True)
    s['bac_phage'] = master_list
    s.close()
    print(len(master_list))


def parse_prot_alg():
    #parses protozoa and algae, there should be 2430 total
    master_list = []
    target_dir = join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Prot_Alg')
    for fi in os.listdir(target_dir):

		#get file data
		file_path =	join(target_dir, fi)
		with open(file_path, 'r') as f:
			html_file = f.read()

		#get the ATCC numbers and make sure there's 100 of them
		m =  pattern.findall(html_file)
		if len(m) != 100:
			print('File %s contains %s entries and not 100' % (fi, len(m)))

		#remove whitespace and add to master list
		m = [s.replace(' ', '') for s in m]
		master_list.extend(m)

    #save list as a shelf
    s = shelve.open(join(ATCC_RAW_FOLDER, 'ATCC_master.db'), writeback=True)
    s['prot_alg'] = master_list
    s.close()
    print(len(master_list))



def parse_fung_yeast():
    #parses fungi and yeast, there should be 58183 total
    master_list = []
    target_dir = join(ATCC_RAW_FOLDER, 'Lists_of_all', 'Fung_Yeast')
    for fi in os.listdir(target_dir):

		#get file data
		file_path =	join(target_dir, fi)
		with open(file_path, 'r') as f:
			html_file = f.read()

		#get the ATCC numbers and make sure there's 100 of them
		m =  pattern.findall(html_file)
		if len(m) != 100:
			print('File %s contains %s entries and not 100' % (fi, len(m)))

		#remove whitespace and add to master list
		m = [s.replace(' ', '') for s in m]
		master_list.extend(m)

    #save list as a shelf
    s = shelve.open(join(ATCC_RAW_FOLDER, 'ATCC_master.db'), writeback=True)
    s['fung_yeast'] = master_list
    s.close()
    print(len(master_list))

parse_bac_phage()
parse_prot_alg()
parse_fung_yeast()
