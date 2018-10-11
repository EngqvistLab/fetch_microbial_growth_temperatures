#!/usr/bin/env python2

#This script was used in the publication doi: https://doi.org/10.1101/271569 
#to open up the data files from the different stock collections and try to match every organism name with a taxonomy ID
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
from urllib2 import urlopen, URLError, HTTPError
from xml.dom import minidom
import time
import os
import shelve
from os.path import join, exists, basename


CURRENT_DIRECTORY = os.getcwd()
PROJ_ROOT_DIRECTORY = '.'
DATA_BASE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external')
RAW_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external')
INTERMEDIATE_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/intermediate')
FINAL_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/final')
TAX_FOLDER = join(PROJ_ROOT_DIRECTORY, 'data/raw_external/taxonomy_data')


if not exists(join(DATA_BASE_FOLDER, 'NCBI_taxonomy')):
	os.makedirs(join(DATA_BASE_FOLDER, 'NCBI_taxonomy'))

if not exists(join(DATA_BASE_FOLDER, 'lineage_data')):
	os.makedirs(join(DATA_BASE_FOLDER, 'lineage_data'))




def filter_entries(in_shelve, out_shelve):
    '''Remove entries with no name or no taxid'''
    print(basename(in_shelve))

    sh = shelve.open(in_shelve)
    input_data = sh['data']
    sh.close()

    counter = 0
    skipped = 0
    retained = 0
    scraps = []
    output_data = []
    for item in input_data:
        counter += 1
        if item['name'] in [None, 'Mixed culture'] or item['taxid'] is None:
            skipped += 1
            scraps.append(item)
            continue
        else:
            retained += 1
            output_data.append(item)

    #open up output shelve and save the clean data
    sh = shelve.open(out_shelve)
    sh['data'] = output_data
    sh.close()

    if exists(join(INTERMEDIATE_FOLDER, 'filtered_scraps.db')):
        scrap_shelve = shelve.open(join(INTERMEDIATE_FOLDER, 'filtered_scraps.db'), writeback=True)
        old_data = scrap_shelve['data']
        scrap_shelve['data'] = old_data + scraps
        scrap_shelve.close()
    else:
        scrap_shelve = shelve.open(join(INTERMEDIATE_FOLDER, 'filtered_scraps.db'))
        scrap_shelve['data'] = scraps
        scrap_shelve.close()

    print('Total %s entries.' % counter)
    print('%s skipped' % skipped)
    print('%s retained' % retained)
    print('')



def filter_all():
    '''Go through each of the stock collection databases and do the filtering'''
    #ATCC data

    print('Filtering ATCC')
    indb = join(INTERMEDIATE_FOLDER, 'ATCC/ATCC_parsed_taxid.db')
    outdb = join(FINAL_FOLDER, 'ATCC/ATCC_parsed_taxid_cleaned.db')
    filter_entries(indb, outdb)

    #DSMZ data
    print('Filtering DSMZ')
    indb = join(INTERMEDIATE_FOLDER, 'DSMZ/DSM_parsed_taxid.db')
    outdb = join(FINAL_FOLDER, 'DSMZ/DSM_parsed_taxid_cleaned.db')
    filter_entries(indb, outdb)

    #NCTC data
    print('Filtering NCTC')
    indb = join(INTERMEDIATE_FOLDER, 'NCTC/NCTC_parsed_taxid.db')
    outdb = join(FINAL_FOLDER, 'NCTC/NCTC_parsed_taxid_cleaned.db')
    filter_entries(indb, outdb)

    #Pasteur data
    print('Filtering Pasteur')
    indb = join(INTERMEDIATE_FOLDER, 'Pasteur/Pasteur_parsed_taxid.db')
    outdb = join(FINAL_FOLDER, 'Pasteur/Pasteur_parsed_taxid_cleaned.db')
    filter_entries(indb, outdb)

    #NIES data
    print('Filtering NIES')
    indb = join(INTERMEDIATE_FOLDER, 'NIES/NIES_parsed_taxid.db')
    outdb = join(FINAL_FOLDER, 'NIES/NIES_parsed_taxid_cleaned.db')
    filter_entries(indb, outdb)

    #BacDive data
    print('Filtering BacDive')
    indb = join(INTERMEDIATE_FOLDER, 'BacDive/BacDive_parsed_taxid.db')
    outdb = join(FINAL_FOLDER, 'BacDive/BacDive_parsed_taxid_cleaned.db')
    filter_entries(indb, outdb)



def get_lineage_xml(TAXONOMY_ID):
    '''Get the whole taxonomic lineage'''
    data_folder = join(DATA_BASE_FOLDER, 'lineage_data', 'data')
    filepath = join(data_folder, '%s.xml' % TAXONOMY_ID)


    # Get the credentials
    with open('credentials.txt', 'r') as f:
        for line in f:
            if line.startswith('TOOL='):
                TOOL = line.strip().split('=')[1]
            elif line.startswith('EMAIL='):
                EMAIL = line.strip().split('=')[1]

    #open file if it exists
    if exists(filepath):
        with open(filepath, 'r') as f:
            xml_data = f.read()

    #otherwise download
    else:
        print('downloading file for %s' % TAXONOMY_ID)
        url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id=%s&retmode=xml&tool=%s&email=%s' % (TAXONOMY_ID, TOOL, EMAIL)
        try:
            xml_data = urllib2.urlopen(url).read()
            with open(filepath, 'w') as f:
                f.write(xml_data)
            time.sleep(1)

        #handle errors
        except HTTPError, e:
            print "HTTP Error:", e.code, url
            return None
        except URLError, e:
            print "URL Error:", e.reason, url
            return None

    return xml_data



def parse_lineage_xml(xml_data):
    '''
    Parse the xml file to get lineage
    '''
    dom = minidom.parseString(xml_data)
    out_data = {}
    domain = None
    lineage_text = dom.getElementsByTagName('Lineage')[0].firstChild.nodeValue

    for item in dom.getElementsByTagName('Taxon'):
        taxid = item.getElementsByTagName('TaxId')[0].firstChild.nodeValue
        name = item.getElementsByTagName('ScientificName')[0].firstChild.nodeValue
        rank = item.getElementsByTagName('Rank')[0].firstChild.nodeValue
        out_data[rank] = (name, taxid)
        if rank == 'superkingdom':
            domain = name

    if 'superkingdom' not in out_data.keys():
        out_data['superkingdom'] = ('NA', 'NA')
    if 'phylum' not in out_data.keys():
        out_data['phylum'] = ('NA', 'NA')
    if 'class' not in out_data.keys():
        out_data['class'] = ('NA', 'NA')
    if 'order' not in out_data.keys():
        out_data['order'] = ('NA', 'NA')
    if 'family' not in out_data.keys():
        out_data['family'] = ('NA', 'NA')
    if 'genus' not in out_data.keys():
        out_data['genus'] = ('NA', 'NA')

    out_data['lineage_text'] = lineage_text
    out_data['lineage_taxid'] ={'superkingdom':out_data['superkingdom'][1], 'phylum':out_data['phylum'][1], 'class':out_data['class'][1], 'order':out_data['order'][1], 'family':out_data['family'][1], 'genus':out_data['genus'][1]}

    if domain == None:
        print(out_data)
        raise ValueError

    return out_data, domain



def get_lineages():
    '''For each valid taxid entry in every dabases, get the lineage'''
    print('Getting lineages')
    folder_n_files = [(join(FINAL_FOLDER, 'ATCC'), 'ATCC_parsed_taxid_cleaned.db'),
                        (join(FINAL_FOLDER, 'DSMZ'), 'DSM_parsed_taxid_cleaned.db'),
                        (join(FINAL_FOLDER, 'NCTC'), 'NCTC_parsed_taxid_cleaned.db'),
                        (join(FINAL_FOLDER, 'Pasteur'), 'Pasteur_parsed_taxid_cleaned.db'),
                        (join(FINAL_FOLDER, 'NIES'), 'NIES_parsed_taxid_cleaned.db'),
                        (join(FINAL_FOLDER, 'BacDive'), 'BacDive_parsed_taxid_cleaned.db')]

    #make a list of unique taxids in my data shelves
    unique_taxid = set([])
    for item in folder_n_files:
        folder, infile = item
        s = shelve.open(join(folder, infile))
        for record in s['data']:
            if record['taxid'] is None:
                continue
            unique_taxid.add(record['taxid'])
        s.close()

    #make a dictionary with each of these organism, use for matching to taxid
    unique_taxid_dict = {key:{} for key in list(unique_taxid)}
    #print(len(unique_taxid_dict.keys()))

    #now match each of the unique taxids using local files
    total = len(unique_taxid_dict.keys())
    counter = 0
    for taxid in unique_taxid_dict.keys():
        if counter % 500 == 0:
            print('%s of %s done' % (counter, total))
        counter += 1

        if taxid in ['1306155']:
            continue

        xml = get_lineage_xml(taxid)
        #print(record['taxid'], record['name'])
        data, domain = parse_lineage_xml(xml)
        unique_taxid_dict[taxid]['domain'] = domain
        unique_taxid_dict[taxid]['lineage'] = data

    #now go through the shelves and assign the already matched taxids
    print('Assigning lineages')
    for item in folder_n_files:
        folder, infile = item
        s = shelve.open(join(folder, infile))
        data = s['data']
        s.close()
        for s in range(0, len(data)):
            taxid = data[s]['taxid']
            if taxid is None:
                print(taxid, s)
            data[s]['domain'] = unique_taxid_dict[taxid]['domain']
            data[s]['lineage'] = unique_taxid_dict[taxid]['lineage']

        s = shelve.open(join(folder, infile.replace('_parsed_taxid', '_parsed_taxid_cleaned')))
        s['data'] = data
        s.close()

    print('Done')




def make_flatfile():
    '''Output filtered data as a flatfile, for each of the databases'''
    folder_n_files = [(join(FINAL_FOLDER, 'ATCC'), 'ATCC_parsed_taxid_cleaned.db', 'ATCC_parsed_taxid_cleaned.txt'),
                        (join(FINAL_FOLDER, 'DSMZ'), 'DSM_parsed_taxid_cleaned.db', 'DSM_parsed_taxid_cleaned.txt'),
                        (join(FINAL_FOLDER, 'NCTC'), 'NCTC_parsed_taxid_cleaned.db', 'NCTC_parsed_taxid_cleaned.txt'),
                        (join(FINAL_FOLDER, 'Pasteur'), 'Pasteur_parsed_taxid_cleaned.db', 'Pasteur_parsed_taxid_cleaned.txt'),
                        (join(FINAL_FOLDER, 'NIES'), 'NIES_parsed_taxid_cleaned.db', 'NIES_parsed_taxid_cleaned.txt'),
                        (join(FINAL_FOLDER, 'BacDive'), 'BacDive_parsed_taxid_cleaned.db', 'BacDive_parsed_taxid_cleaned.txt')]

    for item in folder_n_files:
        folder, infile, outfile = item
        s = shelve.open(join(folder, infile))
        print(infile)
        f = open(join(folder, outfile), 'w')
        f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % ('DB', 'ID', 'Name', 'Temp', 'Risk', 'Domain', 'TaxId', 'Isolation', 'Medium'))
        for record in s['data']:
            db = record['db']
            identifier = record['id']
            name = record['name']
            temp = record['temp']
            risk = record['risk']
            domain = record['type']
            taxid = record['taxid']
            isol = record['isolation']
            medium = record['medium']
            if medium is None or type(medium) is str:
                f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (db, identifier, name, temp, risk, domain, taxid, isol, medium))
            elif type(medium) is list:
                for m in medium:
                    f.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (db, identifier, name, temp, risk, domain, taxid, isol, m))
        s.close()


def compare_databases():
    '''Compare databases to see how many unique exist in each of them'''

    selection_property = 'temp'

    ATCC_orgs = set([])
    s = shelve.open(join(RAW_FOLDER, 'ATCC', 'ATCC_parsed_taxid_cleaned.db'))
    for record in s['data']:
        if record['name'] != None and record[selection_property] != None:
            ATCC_orgs.add(record['name'].lower())
    s.close()

    DSMZ_orgs = set([])
    s = shelve.open(join(RAW_FOLDER, 'DSMZ', 'DSM_parsed_taxid_cleaned.db'))
    for record in s['data']:
        if record['name'] != None and record[selection_property] != None:
            DSMZ_orgs.add(record['name'].lower())
    s.close()

    NCTC_orgs = set([])
    s = shelve.open(join(RAW_FOLDER, 'NCTC', 'NCTC_parsed_taxid_cleaned.db'))
    for record in s['data']:
        if record['name'] != None and record[selection_property] != None:
            NCTC_orgs.add(record['name'].lower())
    s.close()

    Pasteur_orgs = set([])
    s = shelve.open(join(RAW_FOLDER, 'Pasteur', 'Pasteur_parsed_taxid_cleaned.db'))
    for record in s['data']:
        if record['name'] != None and record[selection_property] != None:
            Pasteur_orgs.add(record['name'].lower())
    s.close()

    NIES_orgs = set([])
    s = shelve.open(join(RAW_FOLDER, 'NIES', 'NIES_parsed_taxid_cleaned.db'))
    for record in s['data']:
        if record['name'] != None and record[selection_property] != None:
            NIES_orgs.add(record['name'].lower())
    s.close()

    BacDive_orgs = set([])
    s = shelve.open(join(RAW_FOLDER, 'BacDive', 'BacDive_parsed_taxid_cleaned.db'))
    for record in s['data']:
        if record['name'] != None and record[selection_property] != None:
            BacDive_orgs.add(record['name'].lower())
    s.close()


    #get those that are unique to each db
    all_unique = ATCC_orgs | DSMZ_orgs | NCTC_orgs | Pasteur_orgs | NIES_orgs | BacDive_orgs
    ATCC_unique = ATCC_orgs.difference(DSMZ_orgs | NCTC_orgs | Pasteur_orgs | NIES_orgs | BacDive_orgs)
    DSMZ_unique = DSMZ_orgs.difference(ATCC_orgs | NCTC_orgs | Pasteur_orgs | NIES_orgs | BacDive_orgs)
    NCTC_unique = NCTC_orgs.difference(ATCC_orgs | DSMZ_orgs | Pasteur_orgs | NIES_orgs | BacDive_orgs)
    Pasteur_unique = Pasteur_orgs.difference(ATCC_orgs | DSMZ_orgs | NCTC_orgs | NIES_orgs | BacDive_orgs)
    NIES_unique = NIES_orgs.difference(ATCC_orgs | DSMZ_orgs | NCTC_orgs | Pasteur_orgs | BacDive_orgs)
    BacDive_unique = BacDive_orgs.difference(ATCC_orgs | DSMZ_orgs | NCTC_orgs | Pasteur_orgs | NIES_orgs)

    with open(join(FINAL_FOLDER, 'database_comparison.tsv'), 'w') as f:
        f.write('Database\tOrgs_with_temp\tUnique_to_db\n')
        f.write('%s\t%s\t%s\n' % ('ATCC', len(ATCC_orgs), len(ATCC_unique)))
        f.write('%s\t%s\t%s\n' % ('DSMZ', len(DSMZ_orgs), len(DSMZ_unique)))
        f.write('%s\t%s\t%s\n' % ('NCTC', len(NCTC_orgs), len(NCTC_unique)))
        f.write('%s\t%s\t%s\n' % ('Pasteur', len(Pasteur_orgs), len(Pasteur_unique)))
        f.write('%s\t%s\t%s\n' % ('NIES', len(NIES_orgs), len(NIES_unique)))
        f.write('%s\t%s\t%s\n' % ('BacDive', len(BacDive_orgs), len(BacDive_unique)))
        f.write('%s\t%s\t%s\n' % ('All', len(all_unique), 0))






filter_all() #filter the entries to remove those without a name and those without a taxid
get_lineages() #get lineage for each of the entries
make_flatfile() #outout flatfile
compare_databases() #check how many are unique to each db


