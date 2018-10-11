#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#this script takes NCTC numbers from a list and fetches the html page for that strain
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
import os.path
import re
import os
from os.path import join, exists
import string

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
NCTC_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/NCTC')
NCTC_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/NCTC')
NCTC_FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final/NCTC')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')

if not exists(NCTC_RAW_FOLDER):
	os.makedirs(NCTC_RAW_FOLDER)

if not exists(NCTC_INTERMEDIATE_FOLDER):
	os.makedirs(NCTC_INTERMEDIATE_FOLDER)

if not exists(NCTC_FINAL_FOLDER):
	os.makedirs(NCTC_FINAL_FOLDER)

if not exists(join(NCTC_RAW_FOLDER, 'html_data')):
	os.makedirs(join(NCTC_RAW_FOLDER, 'html_data'))







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


#import the list
def get_exel_exported_data():
	data_list = [] # to hold the data
	f = open(join(NCTC_RAW_FOLDER, 'NCTC_collection.txt'), 'r')
	s = shelve.open(join(NCTC_INTERMEDIATE_FOLDER, 'NCTC_collection.db'))

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

		data['db'] = 'NCTC'
		data['id'] = temp[0].split()[-1]
		data['name'] = temp[1]
		data['temp'] = None
		data['type'] = None
		data['isolation'] = None
		data['risk'] = None

		data_list.append(data)
	s['data'] = data_list
	f.close()
	s.close()



def get_missing_html():
    s = shelve.open(join(NCTC_INTERMEDIATE_FOLDER, 'NCTC_collection.db'))
    for entry in s['data']:
        id = entry['id']
        fname = '%s.html' % id
        if os.path.isfile(join(NCTC_RAW_FOLDER, 'html_data', 'data', fname)) is False:
            #print('getting %s' % fname)
            #build url and fetch page
            url = 'http://www.phe-culturecollections.org.uk/products/bacteria/detail.jsp?refId=NCTC+%s&collection=nctc' % id
            html_file = urllib2.urlopen(url).read() #this returns the result as a string. I'll need to parse it to get the info out.

            #write to file
            f = open(join(NCTC_RAW_FOLDER, 'html_data', 'data', fname), 'w')
            f.write(html_file)
            f.close()
        else:
            #print('not getting %s' % fname)
            pass
    s.close()




def parse_html():
    print('Parsing NCTC')
    s = shelve.open(join(NCTC_INTERMEDIATE_FOLDER, 'NCTC_parsed.db'))
    degree_sign= u'\N{DEGREE SIGN}'

    #make regular expression to find Temp
    re_temp = re.compile(r'''([0-9]+%sC)
    						''' % degree_sign, re.VERBOSE)

    re_temp2 = re.compile(r'''Conditions\sfor\sgrowth\son\s(?:solid|liquid)\smedia:</th>(?:\s)*?
    						<td\sclass="value">(?:\s)*?
    						<span\sitemprop="">(?:\s)*?
    						(?:.)*?
    						,\s?([0-9]+)
    						''', re.VERBOSE)

    re_temp3 = re.compile(r'''Conditions\sfor\sgrowth\son\s(?:solid|liquid)\smedia:</th>(?:\s)*?
    					<td\sclass="value">(?:\s)*?
    					<span\sitemprop="">(?:\s)*?
    					[A-Za-z,.\-_/\\ ()&]*?
    					([0-9]+)
    					''', re.VERBOSE)

    re_name = re.compile(r'''Current\sName:</th>(?:\s)*?
    					<td\sclass="value">(?:\s)*?
    					<span\sitemprop="">(?:\s)*?
    					([A-Za-z,.\-_/\\ ()&]+)
    					''', re.VERBOSE)


    re_previous_name = re.compile(r'''Previous\sCatalogue\sName:</th>(?:\s)*?
    					<td\sclass="value">(?:\s)*?
    					<span\sitemprop="">(?:\s)*?
    					([A-Za-z,.\-_/\\ ()&]+)
    					''', re.VERBOSE)

    re_other_names = re.compile(r'''Other\sNames:</th>(?:\s)*?
    					<td\sclass="value">(?:\s)*?
    					<span\sitemprop="">(?:\s)*?
    					([A-Za-z,.\-_/\\ ()&]+)
    					''', re.VERBOSE)

    re_medium = re.compile(r'''Conditions\sfor\sgrowth\son\s(?:solid|liquid)\smedia:</th>(?:\s)*?
    					<td\sclass="value">(?:\s)*?
    					<span\sitemprop="">(?:\s)*?
    					([A-Za-z,.\-_/\\ ]+)
    					''', re.VERBOSE)

    #make regular expression to find Risk group
    re_risk = re.compile(r'''Hazard\sGroup\s\(ACDP\):</th>(?:\s)*?	#
    						<td\sclass="value">(?:\s)*?				#
    						<span\sitemprop="">(?:\s)*?				#
    						([1-4])								#
    						''', re.VERBOSE)



    #make regular expression to find isolation
    re_isolation = re.compile(r'''Isolated\sFrom:</th>(?:\s)*?
    						<td\sclass="value">(?:\s)*?
    						<span\sitemprop="">(?:\s)*?
    						(.*?)(?:\s)*?
    						</span>
    						''', re.VERBOSE)



	#for i in range(len(s['data'])):
	#	id = s['data'][i]['id']
	#	if id in ['8552', '7564', '7279', '533', '4169', '11873', '11813', '11499', '11497', '11484', '11326', '11298', '11199', '10985', '10984', '10862', '10855', '10716', '10351', '10227', '10182', '10180', '10177', '10171', '10169', '10138', '10132', '10125', '10124']:
	#		continue
    counter = 0
    skipped = 0
    data_list = []
    for filename in os.listdir(join(NCTC_RAW_FOLDER, 'html_data', 'data')):
        counter += 1
        #if counter % 100 == 0:
        #    print(counter)

    	with open(join(NCTC_RAW_FOLDER, 'html_data', 'data', filename), 'r') as f:
    		html_file = f.read()



        db = 'NCTC'
        strain_id = filename.split('.')[0]
        name = None
        previous = None
        other = None
        synonyms = None
        all_names = None
        domain = None
        temperature = None
        risk = None
        isolation = None
        medium = None
        taxid = None

        #get names
        m =  re.search(re_name, html_file)
        if m is not None:
            name = m.group(1)

        m =  re.search(re_previous_name, html_file)
        if m is not None:
            previous = m.group(1)

        m =  re.search(re_other_names, html_file)
        if m is not None:
            other = m.group(1)

        #print(strain_id, name, previous, other)

    	#get the temperature
        if 'Conditions for growth' in html_file:
            m =  re.search(re_temp, html_file)
            if m != None:
                temperature = m.group(1)

            if temperature == None:
                m =  re.search(re_temp2, html_file)
                if m != None:
                    temperature = m.group(1)

            if temperature == None:
                m =  re.search(re_temp3, html_file)
                if m != None:
                    temperature = float(m.group(1))
                else:
                    #print('Error parsing temperature in record %s' % strain_id)
                    skipped += 1
                    #raise ValueError
        else:
            skipped += 1
            #print('no growth data for %s' % strain_id)


    	#get type of organism
    	if 'Bacteria Collection' in html_file:
    		domain = 'bacteria'
    	else:
    		domain = None


    	#get risk group
    	m =  re.search(re_risk, html_file)
    	if m != None:
    		risk = m.group(1)

    	#get isolation site
    	m = re.search(re_isolation, html_file)
    	if m == None:
    		isol = None
    	else:
    		isol = m.group(1)

        #get medium
        m = re.search(re_medium, html_file)
        if m != None:
            medium = m.group(1).rstrip(',')


        #add a record for each name and synonym
        for current_name in set([name, previous, other]):
            if current_name == None:
                continue
            current_name = clean_name(current_name)


        	#put it in the output dictionary
            data = {}
            data['db'] = db
            data['id'] = strain_id
            data['name'] = current_name
            data['temp'] = temperature
            data['type'] = domain
            data['isolation'] = isol
            data['risk'] = risk
            data['medium'] = medium
            data['taxid'] = taxid
            data_list.append(data)

    s['data'] = data_list
    s.close()
    #print('no temperature found for %s out of %s' % (skipped, counter))
    print('Done')


get_exel_exported_data()
get_missing_html()
parse_html()
