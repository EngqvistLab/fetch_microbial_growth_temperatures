#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#this script takes NIES html files and parses them
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

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
NIES_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/NIES')
NIES_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/NIES')
NIES_FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final/NIES')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')

if not exists(NIES_RAW_FOLDER):
	os.makedirs(NIES_RAW_FOLDER)

if not exists(NIES_INTERMEDIATE_FOLDER):
	os.makedirs(NIES_INTERMEDIATE_FOLDER)

if not exists(NIES_FINAL_FOLDER):
	os.makedirs(NIES_FINAL_FOLDER)



import shelve
import os.path
import re
import string


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



def parse_html():
    print('Parsing NIES')
    s = shelve.open(join(NIES_INTERMEDIATE_FOLDER, 'NIES_parsed.db'))

    #make regular expression to find Temp
    re_temp = re.compile(r'''Temperature:\s?([0-9.]+)
    						''', re.VERBOSE)

    re_medium = re.compile(r'''Medium:\s?([\-0-9a-zA-Z ./]+)
    						''', re.VERBOSE)

    re_synonym = re.compile(r'''Synonym[\s]*?
    						</td>
                            [\s]*?
                            <td\scolspan="3">
                            [\s]*?
                            (.*)
                            [\s]*?
                            </td>
    						''', re.VERBOSE)

    re_name = re.compile(r'''Scientific\sname[\S\s]*?
    						<i>([a-zA-Z\s.]*)</i>\s?(?:<i>)?([a-zA-Z\s.]*)
    						''', re.VERBOSE)

    #go through the files and parse
    counter = 0
    skipped = 0
    data_list = []
    for filename in os.listdir(join(NIES_RAW_FOLDER, 'html_data', 'data')):
        if filename.startswith('strainDetailAction.do;'):
            counter += 1
            #if counter % 500 == 0:
            #    print(counter)

            with open(join(NIES_RAW_FOLDER, 'html_data', 'data', filename), 'r') as f:
                html_file = f.read()


            db = 'NIES'
            strain_id = filename.split('=')[-1].replace('.html', '')
            name = None
            synonyms = None
            all_names = None
            domain = None
            temperature = None
            risk = None
            isolation = None
            medium = None
            taxid = None


            #get the degrees
            if 'Temperature:' in html_file:
                m =  re.search(re_temp, html_file)
                assert m != None, 'Error parsing temperature in record %s' % id
                degrees = float(m.group(1))
            else:
                skipped += 1
                continue

            #get name
            m = re.search(re_name, html_file)
            assert m != None, 'Error parsing name of %s' % strain_id
            name = '%s %s' % (m.group(1), m.group(2))

            #get synonyms
            m = re.search(re_synonym, html_file)
            if m != None:
                synonyms = '%s' % m.group(1).split(';')

            #get media
            m = re.search(re_medium, html_file)
            if m != None:
                medium = m.group(1)

            #make a set of the name and synonyms
            if type(synonyms) == list:
                all_names = set([name] + synonyms)
            else:
                all_names = set([name])

            #add a record for each name
            for current_name in all_names:
                current_name = clean_name(current_name)

                data = {}
                data['db'] = 'NIES'
                data['id'] = strain_id
                data['name'] = current_name
                data['temp'] = degrees
                data['type'] = 'algae'
                data['isolation'] = None
                data['risk'] = None
                data['medium'] = medium
                data['taxid'] = taxid
                data_list.append(data)

    s['data'] = data_list
    s.close()
    #print('%s processed' % counter)
    #print('%s skipped' % skipped)
    print('Done')

parse_html()
