#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to download growth temperatures from the BacDive resource.
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


import bacdive
import shelve
import time
import json
import os
from os.path import join, exists
import string

CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
BacDive_RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/BacDive')
BacDive_INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate/BacDive')
BacDive_FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final/BacDive')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')

if not exists(BacDive_RAW_FOLDER):
	os.makedirs(BacDive_RAW_FOLDER)

if not exists(BacDive_INTERMEDIATE_FOLDER):
	os.makedirs(BacDive_INTERMEDIATE_FOLDER)

if not exists(BacDive_FINAL_FOLDER):
	os.makedirs(BacDive_FINAL_FOLDER)

if not exists(join(BacDive_RAW_FOLDER, 'file_lists')):
	os.makedirs(join(BacDive_RAW_FOLDER, 'file_lists'))

if not exists(join(BacDive_RAW_FOLDER, 'json_data')):
	os.makedirs(join(BacDive_RAW_FOLDER, 'json_data'))

if not exists(join(BacDive_RAW_FOLDER, 'file_lists')):
	os.makedirs(join(BacDive_RAW_FOLDER, 'file_lists'))



def clean_name(dirty_name):
    '''
    Clean organism name from "contaminating" characters.
    This is done to better match species names with the ones
    from the other databases.
    '''
    if len(dirty_name.split(' ')) == 1:
        name = dirty_name + ' sp.'
    else:
        name = dirty_name.split(' ')[0] + ' ' + dirty_name.split(' ')[1]

    squeaky_clean = name.replace("'", "").replace('"', '').replace(';', '').replace(':', '')

    #make sure name is ok, without non-ascii characters
    if not all([s in list(string.ascii_lowercase + string.ascii_uppercase + ' .-') for s in squeaky_clean]):
        #print(squeaky_clean)
        return None

    return squeaky_clean


def download_file_lists():
    '''Get lists of available files'''
    print('Downloading file lists.')
    bd_obj = bacdive.BacdiveClient()

    # check how many pages there are (100 records per page)
    num_pages = int(bd_obj.getAllLinks()['count']/100) + 2

    print('There are %s pages.' % num_pages)

    # go through all pages
    for page in range(1, num_pages):

        file_path = join(BacDive_RAW_FOLDER, 'file_lists', 'page_%s.json' % page)

        # skip files that I have
        if exists(file_path):
            #print('not getting page %s' % page)
            continue

        #print('getting page %s' % page)
        response = bd_obj.getAllLinks(page)
        with open(file_path, 'w') as f:
            json.dump(response, f)

	# be kind to the server, take a nap
        time.sleep(1)

    print('Done')


def download_json():
    '''Get json data for all organisms in database'''
    print('Downloading individual files.')

    # make a client to access database
    bd_obj = bacdive.BacdiveClient()

    lists_file_path = join(BacDive_RAW_FOLDER, 'file_lists')

    # go through all pages
    for fi in sorted(os.listdir(lists_file_path)):
        if fi.endswith('.json') is False:
            continue
        #print('from page %s' % fi)

        #read the file lists in order
        with open(join(lists_file_path, fi), 'r') as f:
            response = json.loads(f.read())

        for result in response['results']:

            #get json data for each of the 100 urls in every page
            url = result['url']

            id = url.split('/')[-2]
            file_path = join(BacDive_RAW_FOLDER, 'json_data', 'data', '%s.json' % id)

            #skip files that I have
            if exists(file_path):
                #print('not getting %s' % id)
                continue

            print('getting %s' % id)
            json_data = bd_obj.getSpecificInfo(url)
            with open(file_path, 'w') as f:
                json.dump(json_data, f)

            time.sleep(1)

    print('Done')


def parse_json():
    '''Parse json files and output a shelve'''
    print('Parsing BacDive json files')

    s = shelve.open(join(BacDive_INTERMEDIATE_FOLDER, 'BacDive_parsed.db'))

    data_list = [] # to hold the data
    target_folder = join(BacDive_RAW_FOLDER, 'json_data', 'data')
    for filename in sorted(os.listdir(target_folder)):

        #skip files that are not json
        if filename.endswith('.json') is False:
            continue

        #load the data
        with open(join(target_folder, filename)) as f:
            json_data = json.loads(f.read())


        db = 'BacDive'
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



        if json_data['taxonomy_name'].get('strains_tax_PNU') is not None:
            name = str(json_data['taxonomy_name']['strains_tax_PNU'][0]['species'])
            domain = str(json_data['taxonomy_name']['strains_tax_PNU'][0]['domain'])
        elif json_data['taxonomy_name'].get('strains') is not None:
            name = str(json_data['taxonomy_name']['strains'][0]['species'])
            domain = str(json_data['taxonomy_name']['strains'][0]['domain'])
        else:
            print(json_data['taxonomy_name'])

        #get medium
        if json_data.get('culture_growth_condition') is not None:
            if json_data['culture_growth_condition'].get('culture_medium') is not None:
                if json_data['culture_growth_condition']['culture_medium'][0]['medium_growth'] == True:
                    medium = str(json_data['culture_growth_condition']['culture_medium'][0]['media_link'])

        #get temperature
        if json_data['culture_growth_condition'].get('culture_temp') is not None:
            if json_data['culture_growth_condition']['culture_temp'][0]['ability'] == 'positive':
                temperature = json_data['culture_growth_condition']['culture_temp'][0]['temp']
                try:
                    temperature = float(temperature)
                except:
                    a, b = temperature.replace(' ', '').split('-')
                    temperature = round((float(a)+float(b))/2)

        #get isolation
        if json_data.get('environment_sampling_conditions_isolation_source') is not None:
            if json_data['environment_sampling_conditions_isolation_source'].get('origin') is not None:
                source = json_data['environment_sampling_conditions_isolation_source']['origin'][0]['sample_type']


        #get risk category

        data = {}
        data['db'] = db
        data['id'] = strain_id
        data['name'] = clean_name(name)
        data['type'] = domain
        data['risk'] = risk
        data['isolation'] = isolation
        data['temp'] = temperature
        data['medium'] = medium
        data['taxid'] = taxid
        data_list.append(data)



    #shelve file
    s['data'] = data_list
    s.close()
    print('Done')

download_file_lists()
download_json()
parse_json()
