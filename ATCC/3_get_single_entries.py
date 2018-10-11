#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to make use of the data shelve with ATCC numbers that I generated from strain lists.
#it takes each individual number and fetches the html page for that entry
#these pages will be parsed later to get info on strain names and growth temperatures
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
import urllib2
from os.path import join, exists, isfile
import os

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
ATCC_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/ATCC')
ATCC_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/ATCC')
ATCC_FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final/ATCC')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')


def get_prot_alg():
    print('Getting prot_alg')
    for i in range(len(s['prot_alg'])):
        if i % 100 == 0:
            print('%s of %s' % (i, len(s['prot_alg'])))

        id = s['prot_alg'][i]

        #check whether I have file already
        target_file = join(ATCC_RAW_FOLDER, 'Prot_Alg', '%s.html' % id)
        if isfile(target_file):
            print('not getting %s' % id)
            continue

        print('getting %s' % id)
        #build url and fetch page
        url = 'http://www.lgcstandards-atcc.org/Products/All/%s.aspx#generalinformation/' % id
        file = urllib2.urlopen(url).read() #this returns the result as a string. I'll need to parse it to get the info out.
        assert str(id) in file, 'Error id %s not in file (index %s)' % (id, i)

        #write to file
        f = open(target_file, 'w')
        f.write(file)
        f.close()
    print('Done')


def get_bac_phage():
    #bacteria and phage, 17916 total
    print('Getting bac_phage')
    for i in range(0, len(s['bac_phage'])):
        if i % 100 == 0:
            print('%s of %s' % (i, len(s['bac_phage'])))

        id = s['bac_phage'][i]
        if len(id) > 12:
            print('Bad id at position %s: %s' % (i, id))
            continue

        #check whether I have file already
        target_file = join(ATCC_RAW_FOLDER, 'Bac_Phage', '%s.html' % id)
        if isfile(target_file):
            print('not getting %s' % id)
            continue

        print('getting %s' % id)
        #build url and fetch page
        url = 'http://www.lgcstandards-atcc.org/Products/All/%s.aspx#generalinformation/' % id
        file = urllib2.urlopen(url).read() #this returns the result as a string. I'll need to parse it to get the info out.
        assert str(id) in file, 'Error id %s not in file (index %s)' % (id, i)

        #write to file
        f = open(target_file, 'w')
        f.write(file)
        f.close()
    print('Done')


def get_fung_yeast():
    #fungi and yeast, 55200 total
    print('Getting fung_yeast')
    length = len(s['fung_yeast'])
    for i in range(length):
        if i % 100 == 0:
            print('%s of %s' % (i, length))

        id = s['fung_yeast'][i]
        if len(id) > 12:
            print('Bad id at position %s: %s' % (i, id))
            continue

        #check whether I have file already
        target_file = join(ATCC_RAW_FOLDER, 'Fung_Yeast', '%s.html' % id)
        if isfile(target_file):
            print('not getting %s' % id)
            continue

        #build url and fetch page
        print('getting %s' % id)
        url = 'http://www.lgcstandards-atcc.org/Products/All/%s.aspx#generalinformation/' % id
        file = urllib2.urlopen(url).read() #this returns the result as a string. I'll need to parse it to get the info out.
        assert str(id) in file, 'Error id %s not in file (index %s)' % (id, i)

        #write to file
        f = open(target_file, 'w')
        f.write(file)
        f.close()
    print('Done')



#read in the shelve to get data on which ids need to be downloaded
s = shelve.open(join(ATCC_RAW_FOLDER, 'ATCC_master.db'))

get_prot_alg()
get_bac_phage()
get_fung_yeast()

s.close()
