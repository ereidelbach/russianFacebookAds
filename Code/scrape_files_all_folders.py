#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 10 11:55:23 2018

@author: ejreidelbach

:DESCRIPTION:

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import csv
import os  
from tabula import read_pdf
import json
#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/russianFacebookAds/Data')

# Read in all directories (i.e. folders) containing Russion Facebook Ad data
directories = [d[0] for d in os.walk('.')]
directories = sorted(directories)

# create a list for storaing ads across all months
ad_list_master = []

# Iterate through each quarter's folder
for dir in directories:
    
    # Announce what directory (i.e. folder) we're in
    print("Working in directory: " + dir)
        
    # Read in all PDF Files
    files = [f for f in os.listdir(dir) if f.endswith(('.pdf'))]
    files = sorted(files)
    
    ad_list = []
    # Read in the ad contained within every file in the directory
    for f in files:
        fname = dir.strip('./') + "/" + f
        print('Reading in file: ' + fname)
        
        #######################################################################
        # AD INFO ONLY --> No picture info
        #######################################################################
        
        # Read in the PDF (only the first page of ad info, not the picture)
        ad = read_pdf(fname, guess=False)
    
        values_list = []
        value = ''
        
        # Create the Ad Filename value
        values_list.append('Ad Filename ' + '/' + fname)
        
        # Grab the Ad Id
        add_id = ad.columns[0].strip('Ad ID ')
        if add_id == '':
            add_id = ad.columns[0].strip('Ad I D')
        values_list.append('Ad ID' + ' ' + ad.columns[0].strip('Ad I D '))
        
        # Grab all other Ad information
        for index, row in ad.iterrows():
            if type(row[0]) is float:
                pass
            elif row[0].startswith('Ad '):
                if value != '':
                    values_list.append(value)
                value = row[0]    
            else:
                value = value + ' ' + row[0]
        values_list.append(value)        
        
        # Remove any unnecessary text from the last value which may get picked
        #   up by the PDF scanner
        values_list[-1] = values_list[-1].split(' Redactions')[0]
        
        # Add the contents of each ad to a dictionary
        ad_dict = {}
        for value in values_list:
            if value.startswith('Ad ID'):
                ad_dict['ID'] = value.split('Ad ID ')[1]
            elif value.startswith('Ad Filename'):
                ad_dict['source_file'] = value.split('Ad Filename ')[1]            
            elif value.startswith('Ad Text'):
                try:
                    ad_dict['text'] = value.split('Ad Text ')[1]
                except:
                    ad_dict['text'] = value.split('Ad Text')[1]
            # Some Landing Page values have been redacted
            elif value.startswith('Ad Landing Page'):
                try:
                    ad_dict['landing_page'] = value.split('Ad Landing Page ')[1]
                except:
                    ad_dict['landing_page'] = "REDACTED"
            elif value.startswith('Ad Targeting'):
                ad_dict['targeting'] = value.split('Ad Targeting ')[1]
            elif value.startswith('Ad Impressions'):
                ad_dict['impressions'] = value.split('Ad Impressions ')[1]
            elif value.startswith('Ad Clicks'):
                ad_dict['clicks'] = value.split('Ad Clicks ')[1]
            elif value.startswith('Ad Spend'):
                if value == 'Ad Spend None':
                    ad_dict['spend'] = 0
                    ad_dict['spend_currency'] = 'N/A'
                else:
                    ad_dict['spend'] = value.split('Ad Spend ')[1].split(' ')[0]
                    try:
                        ad_dict['spend_currency'] = value.split('Ad Spend ')[1].split(' ')[1]
                    except:
                        ad_dict['spend_currency'] = 'N/A'
            elif value.startswith('Ad Creation Date'):
                ad_dict['date_creation'] = value.split('Ad Creation Date ')[1]
            elif value.startswith('Ad End Date'):
                ad_dict['date_end'] = value.split('Ad End Date ')[1]

        # Search for any subcategories in `Ad Targeting` and extract them
        sub_categories = []
        for word in ad_dict['targeting'].split(' '):
            if ':' in word:
                sub_categories.append(word.replace(':',''))
        targeting_list = []
        for i in range(0,len(sub_categories)):
            dict_key = 'target_' + sub_categories[i].lower()
            if i < len(sub_categories) - 1:
                ad_dict[dict_key] = ad_dict['targeting'].split(
                        sub_categories[i] + ': ')[1].split(sub_categories[i+1] + ': ')[0]
            else:
                ad_dict[dict_key] = ad_dict['targeting'].split(
                        sub_categories[i] + ': ')[1]
        
        # Remove the original `Ad Targeting` key as it is redundant now
        del ad_dict['targeting']
        
        # Create a directory that identifies from where each zip file originated
        source_dict = {'2015-06':'2015-q2.zip',
                       '2015-07':'2015-q3.zip',
                       '2015-08':'2015-q3.zip',
                       '2015-09':'2015-q3.zip',
                       '2015-10':'2015-q4.zip',
                       '2015-11':'2015-q4.zip',
                       '2015-12':'2015-q4.zip',
                       '2016-01':'2016-q1.zip',
                       '2016-02':'2016-q1.zip',
                       '2016-03':'2016-q1.zip',
                       '2016-04':'2016-q2.zip',
                       '2016-05':'2016-q2.zip',
                       '2016-06':'2016-q2.zip',
                       '2016-07':'2016-q3.zip',
                       '2016-08':'2016-q3.zip',
                       '2016-09':'2016-q3.zip',
                       '2016-10':'2016-q4.zip',
                       '2016-11':'2016-q4.zip',
                       '2016-12':'2016-q4.zip',
                       '2017-01':'2017-q1.zip',
                       '2017-02':'2017-q1.zip',
                       '2017-03':'2017-q1.zip',
                       '2017-04':'2017-04.zip',
                       '2017-05':'2017-05.zip',
                       '2017-08':'2017-q3.zip',
                       '2017-09':'2017-q3.zip',
                       }
        
        # Insert the original source zip file based on the folder
        ad_dict['source_zip'] = source_dict[dir.strip('./')]
         
        #######################################################################
        # PICTURE INFO --> Information about the actual ad image on Facebook
        #######################################################################

        # Read in the PDF (only the first page of ad info, not the picture)
        #   Some pages do not have picture information so we have a try/except
        #   to catch the resulting errors from scanning page 2
        try:
            pic = read_pdf(fname, pages=2, guess=False)
        except:
            continue
    
        value = ''
                
        # Grab all the picture information from the first column of the dataframe
        pic_data = pic[pic.columns[0]]
        
        catch_list = ['people like', 
                      'Likes', 
                      'person likes', 
                      'Shares',
                      'people We this',
                      ]
        stats = ''
        for data in pic_data:
            if type(data) == float:
                pass
            elif any(word in data for word in catch_list):
                stats = data
                break
        ad_dict['pic_stats'] = stats
            

        #######################################################################
        # Add the dictionary to both lists containing ad information
        ad_list.append(ad_dict)
        ad_list_master.append(ad_dict)        
    
    ###########################################################################
    # Output the monthly list to a file
    if len(ad_list) > 0:
        output_fname = dir + '.json'
        with open(output_fname, 'wt') as out:
            json.dump(ad_list, out, sort_keys=True, indent=4, separators=(',', ': '))

###############################################################################
# Output the comprehensive list to a file
if len(ad_list_master) > 0:
    output_fname = 'all_months.json'
    with open(output_fname, 'wt') as out:
        json.dump(ad_list_master, out, sort_keys=True, indent=4, separators=(',', ': '))