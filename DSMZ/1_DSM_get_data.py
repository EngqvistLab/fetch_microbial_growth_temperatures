#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to download html files containing growth temperatures from the DSMZ resource.
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
import shelve
import os
from os.path import join, exists, isfile
import time
import re
import time
import string

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
DSMZ_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/DSMZ/')
DSMZ_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/DSMZ/')
DSMZ_FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final/DSMZ/')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')

if not exists(DSMZ_RAW_FOLDER):
	os.makedirs(DSMZ_RAW_FOLDER)

if not exists(DSMZ_INTERMEDIATE_FOLDER):
	os.makedirs(DSMZ_INTERMEDIATE_FOLDER)

if not exists(DSMZ_FINAL_FOLDER):
	os.makedirs(DSMZ_FINAL_FOLDER)



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


def get_exel_exported_data():
	'''
	Opens the file I got from DSMZ, parses it and stores at a python shelve.
	'''
	s = shelve.open(join(DSMZ_INTERMEDIATE_FOLDER, 'DSM_collection.db'))
	f = open(join(DSMZ_RAW_FOLDER, 'DSMZStrainsWithGrowthTemp.txt'), 'r')

	data_list = [] # to hold the data
	firstline = True
	for line in f:
		#skip first line
		if firstline is True:
			firstline = False
			continue

		data = {}
		line = line.replace('\n', '')
		line = line.replace('_', ' ')
		temp = line.split('\t')

		data['db'] = 'DSM'
		data['id'] = temp[0]
		data['name'] = temp[1]
		data['temp'] = float(temp[2])
		data['type'] = temp[3]
		data['isolation'] = None
		data['risk'] = None

		data_list.append(data)
	f.close()

	#shelve file
	s['data'] = data_list
	s.close()
	#print('Done')



def get_html_files():
    '''
    Get html records based on organism ids. Just because they are good to have in case I want more info.
    '''

    s = shelve.open(join(DSMZ_INTERMEDIATE_FOLDER, 'DSM_collection.db'))

    for entry in s['data']:
        id = entry['id']
        fname = '%s.html' % id
        target_file = join(DSMZ_RAW_FOLDER, 'html_data', 'data', fname)
        if isfile(target_file) is False:
            #print('getting DSM %s' % id)

            #build url and fetch page
            url = 'http://www.dsmz.de/catalogues/details/culture/DSM-%s.html' % id
            html_data = urllib2.urlopen(url).read() #this returns the result as a string. I'll need to parse it to get the info out.

            #write to file
            f = open(target_file, 'w')
            f.write(html_data)
            f.close()

            time.sleep(1)
        else:
            #print('not getting DSM %s' % id)
            pass
    s.close()



def parse_html_files():
    print('Parsing DSM')
    s = shelve.open(join(DSMZ_INTERMEDIATE_FOLDER, 'DSM_parsed.db'))


    #make regular expression to find Risk group
    re_risk = re.compile(r'''<dt>Risk\sgroup:\s</dt>\s*?	#<dt>Risk group: </dt>
    						<dd>(<strong>)?				# <dd>
    						([1-4])							#numbers 1 to 4
    						''', re.VERBOSE)

    #make regular expression to find isolation
    re_isolation = re.compile(r'''<dt>Isolated\sfrom:\s</dt>\s*		#<dt>Isolated from: </dt>
    						 <dd>(.*?)</dd>								#<dd>.+</dd> with anything inside
    						''', re.VERBOSE)

    name_pattern = re.compile(r'''Name:\s</strong></dt>\s*?<dd><strong>
                                    <i>(.*?)</i></strong>\s*?<strong><i>(.*?)</i>''', re.VERBOSE)

    name_pattern2 = re.compile(r'''Name:\s</strong></dt>\s*?<dd><strong>
                                    <i>(.*?)</i></strong>\s*?<strong>(.*?)</strong>''', re.VERBOSE)

    name_pattern3 = re.compile(r'''Species:\s</strong></dt>\s*?<dd><strong>
                                    <i>(.*?)</i>''', re.VERBOSE)

    name_pattern4 = re.compile(r'''Name:\s</strong></dt>\s*?<dd>[']*<strong>
                                    <i>(.*?)</i>''', re.VERBOSE)

    synonym_section_pattern = re.compile(r'''Synonym[(]*s[)]*:\s</dt>\s*?<dd>([\s\S]*?)</dd>
                                    ''', re.VERBOSE)

    synonym_names_pattern = re.compile(r'''[']+<i>([a-zA-Z0-9 \.]+?)</i>[']+''', re.VERBOSE)

    synonym_names_pattern2 = re.compile(r'''<i>([a-zA-Z0-9 \.]+?)</i>\s*?<i>([a-zA-Z0-9 \.]+?)</i>''', re.VERBOSE)

    growth_pattern = re.compile(r'''Cultivation\sconditions:\s</dt>\s
                                    *?<dd><a \shref="(.*?)"\s   #html link to medium
                                    class="download">(.*?)</a>  #media name
                                    ,*\s*([0-9\\-]+)               #temperature
                                    ''', re.VERBOSE)



    #go through the files and parse
    counter = 0
    skipped = 0
    data_list = []
    for filename in os.listdir(join(DSMZ_RAW_FOLDER, 'html_data', 'data')):
        counter += 1
        #if counter % 500 == 0:
        #    print(counter)

        with open(join(DSMZ_RAW_FOLDER, 'html_data', 'data', filename), 'r') as f:
            html_file = f.read()


        if 'PLASMIDS' in html_file or 'PHAGES' in html_file:
            continue

        db = 'DSMZ'
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

        #get risk group
        m =  re.search(re_risk, html_file)
        if m != None:
            risk = m.group(2)

        #get isolation site
        m = re.search(re_isolation, html_file)
        if m != None:
            isolation = m.group(1)

        #get name
        m = re.search(name_pattern, html_file)
        if m != None:
            name = m.group(1) + ' ' + m.group(2)
        else:
            m = re.search(name_pattern2, html_file)
            if m != None:
                name = m.group(1) + ' ' + m.group(2)
            else:
                m = re.search(name_pattern3, html_file)
                if m != None:
                    name = m.group(1)
                else:
                    m = re.search(name_pattern4, html_file)
                    if m != None:
                        name = m.group(1)


        #get synonyms
        synonym_part = None
        synonyms1 = []
        synonyms2 = []
        m = re.search(synonym_section_pattern, html_file)
        if m != None:
            synonym_part = m.group(1)
            m = re.search(synonym_names_pattern, synonym_part)
            if m != None:
                synonyms1 = [m.group(1), ]


            synonyms2 = re.findall(synonym_names_pattern2, synonym_part)
            synonyms2 = [part[0] + ' ' + part[1] for part in synonyms2]
        synonyms = synonyms1 + synonyms2


        #get temperature
        m = re.search(growth_pattern, html_file)
        if m != None:
            #medium = set([m.group(1)]
            #medium_name = m.group(2)
            temperature = m.group(3)
            try:
                temperature = float(temperature)
            except:
                if len(temperature.split('-')) == 2:
                    a, b = temperature.split('-')
                else:
                    print(temperature)
                temperature = round((float(a)+float(b))/2)


        #get medium
        medium = re.findall('http://www.dsmz.de/microorganisms/medium/pdf/DSMZ_Medium[0-9]+.pdf', html_file)
        if medium == set([]):
            medium = None

        #get domain
        if 'FUNGI' in html_file:
            domain = 'fungi'
        elif 'BACTERIA' in html_file:
            domain = 'bacteria'
        elif 'ARCHAEA' in html_file:
            domain = 'archaea'
        else:
            domain = None


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



get_exel_exported_data()
get_html_files()
parse_html_files()
