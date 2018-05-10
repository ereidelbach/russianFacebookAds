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
        print('Reading in file: ' + f)
        ad = read_pdf(dir + "/" + f, guess=False)
    
        values_list = []
        value = ''
        
        # Create the Ad Filename value
        values_list.append('Ad Filename ' + dir + '/' + f)
        
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
            if value.startswith('Ad Filename'):
                ad_dict['Ad Filename'] = value.split('Ad Filename ')[1]            
            elif value.startswith('Ad ID'):
                ad_dict['Ad ID'] = value.split('Ad ID ')[1]
            elif value.startswith('Ad Text'):
                try:
                    ad_dict['Ad Text'] = value.split('Ad Text ')[1]
                except:
                    ad_dict['Ad Text'] = value.split('Ad Text')[1]
            elif value.startswith('Ad Landing Page'):
                ad_dict['Ad Landing Page'] = value.split('Ad Landing Page ')[1]
            elif value.startswith('Ad Targeting'):
                ad_dict['Ad Targeting'] = value.split('Ad Targeting ')[1]
            elif value.startswith('Ad Impressions'):
                ad_dict['Ad Impressions'] = value.split('Ad Impressions ')[1]
            elif value.startswith('Ad Clicks'):
                ad_dict['Ad Clicks'] = value.split('Ad Clicks ')[1]
            elif value.startswith('Ad Spend'):
                ad_dict['Ad Spend'] = value.split('Ad Spend ')[1]
            elif value.startswith('Ad Creation Date'):
                ad_dict['Ad Creation Date'] = value.split('Ad Creation Date ')[1]
            elif value.startswith('Ad End Date'):
                ad_dict['Ad End Date'] = value.split('Ad End Date ')[1]

        # Search for any subcategories in `Ad Targeting` and extract them
        sub_categories = []
        for word in ad_dict['Ad Targeting'].split(' '):
            if ':' in word:
                sub_categories.append(word.replace(':',''))
        targeting_list = []
        for i in range(0,len(sub_categories)):
            dict_key = 'Ad Targeting - ' + sub_categories[i]
            if i < len(sub_categories) - 1:
                ad_dict[dict_key] = ad_dict['Ad Targeting'].split(
                        sub_categories[i] + ': ')[1].split(sub_categories[i+1] + ': ')[0]
            else:
                ad_dict[dict_key] = ad_dict['Ad Targeting'].split(
                        sub_categories[i] + ': ')[1]
        
        # Remove the original `Ad Targeting` key as it is redundant now
        del ad_dict['Ad Targeting']
         
        # Add the dictionary to a list containing all ad information
        ad_list.append(ad_dict)
        
    # Output the list to a file
    output_fname = dir + '.json'
    with open(output_fname, 'wt') as out:
        json.dump(ad_list, out, sort_keys=True, indent=4, separators=(',', ': '))