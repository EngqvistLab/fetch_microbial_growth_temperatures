#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to parse the individual ATCC entries and extracts strain name, growth temp and isolation (if available)
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
from os.path import join, exists, isfile
import string


CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
ATCC_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/ATCC')
ATCC_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/ATCC')



#make regular expression for replacing html tags
temp_pattern = re.compile(r'''Temperature:\s*?(?:<strong>|</strong>|</b>)(.*?)(&deg;)?C''', re.VERBOSE)
temp_pattern1 = re.compile(r'''<div>Temperature:(.*?)(&deg;)?C</div>''', re.VERBOSE)
temp_pattern2 = re.compile(r'''Temperature:(.*?)(C<|C\n)''', re.VERBOSE)
temp_pattern3 = re.compile(r'''Temperature:(.*?)C''', re.VERBOSE)
temp_pattern4 = re.compile(r'''>(.*?)&deg;C''', re.VERBOSE)

isolation_pattern = re.compile(r'''<th>\s*?Isolation\s*?</th>\s*?<td>\s*?<div>(.*?)</div>  #comment
						''', re.VERBOSE)

strain_pattern = re.compile(r'''name="description"\scontent="(.*?)ATCC\s''', re.VERBOSE)
strain_pattern1 = re.compile(r'''<title>\s*?(.*?)\n?\s?ATCC\s*?''', re.VERBOSE)
strain_pattern2 = re.compile(r'''<I>(.*?)</I>.*?ATCC<sup>&reg;''', re.VERBOSE)
strain_pattern3 = re.compile(r'''<I>(.*?)</I>''', re.VERBOSE)

risk_pattern = re.compile(r'''Biosafety Level\s*?</th>\s*?<td>\s*?([1-4])\s*?</td>''')

synonym_patttern = re.compile(r'''Deposited\s[aA]s\s*</th>\s*<td>\s*<I>(.*?)</I>''')

medium_pattern = re.compile(r'''(Medium\s[0-9]+):''')



def clean_name(dirty_name):
    '''Clean bacterial name from contaminating characters.'''
    if len(dirty_name.split(' ')) == 1:
        name = dirty_name + ' sp.'
    else:
        name = dirty_name.split(' ')[0] + ' ' + dirty_name.split(' ')[1]

    squeaky_clean = name.replace("'", "").replace('"', '').replace(';', '').replace(':', '')

    #make sure name is ok
    if not all([s in list(string.ascii_lowercase + string.ascii_uppercase + ' .-') for s in squeaky_clean]):
        #print(squeaky_clean)
        return None

    return squeaky_clean



def parse():
    print('Parsing ATCC')
    s = shelve.open(join(ATCC_INTERMEDIATE_FOLDER, 'ATCC_parsed.db'))

    data_list = []
    for folder in ['Bac_Phage', 'Fung_Yeast', 'Prot_Alg']:
        counter = 0
        skipped = 0

        for filename in os.listdir(join(ATCC_RAW_FOLDER, folder, 'data')):
            counter += 1
            #if counter % 500 == 0:
            #    print(counter)


            with open(join(ATCC_RAW_FOLDER, folder, 'data', filename), 'r') as f:
                html_page = f.read()

            db = 'ATCC'
            strain_id = filename.split('.')[0]
            name = None
            synonyms = None
            all_names = None
            domain = None
            temperature = None
            risk = None
            isolation = None
            medium = None
            taxid = None

            #get temperature, if not present, skip record
            if 'Temperature:' in html_page:
                m = temp_pattern.search(html_page)
                if m == None:
                    m = temp_pattern1.search(html_page)
                    #print('alternate temp for %s' % strain_id)
                    if m == None:
                        m = temp_pattern2.search(html_page)
                        #print('alternate temp 2 for %s' % strain_id)
                        if m == None:
                            m = temp_pattern3.search(html_page)
                            #print('alternate temp 3 for %s' % strain_id)
                            if m == None:
                                m = temp_pattern4.search(html_page)
                                #print('alternate temp 4 for %s' % strain_id)
                assert m != None, 'Error, Temperature word found but incorrect parsing in file %s' % strain_id

                #get the temperature and convert to float
                temperature = m.group(1).replace('&nbsp;', '').replace(';', '').replace('</strong>', '').replace('&deg', '').replace(',', '').replace(' ', '').replace('%', '').replace('</strong', '').replace('deg', '').replace('C', '').replace('<strong>', '')
                temperature = temperature.decode('utf-8').replace(u'\xb0', u'').encode('utf-8')

                try:
                    temperature = float(temperature)
                except:
                    if len(temperature.split('-')) == 2:
                        a, b = temperature.split('-')
                    elif len(temperature.split('to')) == 2:
                        a, b = temperature.split('to')
                    else:
                        print(temperature)
                    temperature = round((float(a)+float(b))/2)

            else:
                continue

            #get strain name
            m = strain_pattern.search(html_page)
            if m == None:
                m = strain_pattern1.search(html_page)
                #print('Alternate name for %s' % strain_id)
                if m == None:
                    m = strain_pattern2.search(html_page)
                    #print('Alternate name 2 for %s' % strain_id)
                    if m == None:
                        m = strain_pattern3.search(html_page)
                        #print('Alternate name 3 for %s' % strain_id)
            assert m != None, 'Error, Name not parsed in file %s' % strain_id
            name = m.group(1)

            #get isolation
            m = isolation_pattern.search(html_page)
            if m != None:
                isolation = m.group(1)

            #get risk
            m = risk_pattern.search(html_page)
            if m != None:
                risk = m.group(1)

            #get medium
            m = medium_pattern.search(html_page)
            if m != None:
                medium = m.group(1)

            #get synonyms
            synonyms = []
            m = synonym_patttern.search(html_page)
            if m != None:
                synonyms = [m.group(1), ]

            #add one entry for each stran name (including synonyms)
            all_names = set([name] + synonyms)
            for current_name in all_names:
                if current_name == None:
                    continue
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
    s['data'] = data_list
    s.close()
    print('Done')


parse()

