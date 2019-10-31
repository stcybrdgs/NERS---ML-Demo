# -*- coding: utf-8 -*-
'''
Monday, August 12, 2019
Stacy Bridges
-   REM THIS SCRIPT HAS DIFFERENT API FRONT END THAN api_inces-backend_2.py
-	this script makes GET request from ince's backend (brammer, rs)
	https://api.ince.live/product?apikey=4f032b1a18ab3f36&id=6001&brand=skf
- 	the data pulled from the api is output to an excel spreadsheet (.xlsx)

APIKey = hardcoded for now
ID = the search string. Exact matches only but ignores special characters. Not case sensitive.
Brand = optional

//////////////
Brammer xls fields:
Category		Brand	Manufacturer PartNo		Brammer Web ID		Description		Details

example:
{
	"id":"Brammer:100901675805",
	"source":"Brammer",
	"supplierID":"100901675805",
	"brand":"HIMALAYAN",
	"manufacturerID":"3100-13",
	"searchID":"310013",
	"description":"HIMALAYAN 3100 SAFETY BOOT BLACK SIZE 13",
	"details":"",
	"productCategory":"Tools and Maintenance Products >> Personal Protection Equipment (PPE) >> Footwear >> Safety Boots \r"

}

//////////////
RS xls fields:
Category		Brand	Manufacturer Part No	RS Stock No			Description	 	Price 		Unit

example:
{
	"id":"RS:543-737",
	"source":"RS",
	"supplierID":"543-737",
	"brand":"Richco",
	"manufacturerID":"TCBS 8 01",
	"searchID":"TCBS801",
	"description":"TCBS 8 01, 12.7mm High Nylon Standard PCB Support Pillar With 4mm PCB Hole and 4mm Chassis Hole for M3.5 Screw",
	"details":null,
	"productCategory":"PCB Support Pillars"
}

'''
# IMPORTS  ---------------------------------------------------------
import csv
import requests
import pandas as pd
from pandas import ExcelWriter
import numpy as np
import sys
import io

# UTF-8 Encoding  --------------------------------------------------
# allow printing of special characters to console without error
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

# GLOBALS  ---------------------------------------------------------
mMats_test = []
mMats = []

# FUNCTIONS  -------------------------------------------------------
def import_csv(d):
	code = ''
	with open(d) as data:
		csv_reader = csv.reader(data, delimiter='|')
		i = 0
		for row in csv_reader:
			if i > 0:
				if len(row) == 0:
					code = ''
				else:
					code = row[0]
				mMats.append(code)
			i += 1
    # end function //

# MAIN  ------------------------------------------------------------
def main():
	# config  ------------------------------------------------------\\
	test = False
	mMats_test = [
		'6001','9964', 'BES 516-325-S4-C', '',
		'6310', '9982','6001', '6836','6219Z','6220Z','6019Z','',
		'6014M','6310M','6217MC3','6311M','6314MC3']

	# config  ------------------------------------------------------//

	# define path to input file
	inFile = r'C:/Users/stacy/My GitHub/wxMatchingEngine/store/model/brmr_erp1/nu_demo/api_ince_backend_search_ids.csv'

	# define path to output file
	outFile = 'C:/Users/stacy/My GitHub/wxMatchingEngine/store/model/brmr_erp1/nu_demo/api_ince_backend_out.xlsx'
	outFile_test = 'C:/Users/stacy/My GitHub/wxMatchingEngine/store/model/brmr_erp1/nu_demo/api_ince_backend_out_test.xlsx'

	if test == True:
		pdFile = outFile_test
	else:
		pdFile = outFile

	# external id inputs
	import_csv(inFile)

	# clean special characters and spaces from codes in mMats[]
	special_chars = ['\\','/','-','.','_','+','"']
	i = 0
	for code in mMats:
		for char in special_chars:
			mMats[i] = code.strip().replace(char, '')
		i += 1

	# setup pandas containers to hold contents of xlsx columns
	# wBrand    |  wManufacturerPartNo  |  wSupplierId    |  wSource    |  wDescription    |  wDetails   |  wCategory
	# p_brands  |  p_manufacturerIds    |  p_supplierIds  |  p_sources  |  p_descriptions  |  p_details  |  p_categories
	p_searchIds = []  # field for search code to help align results to target xlsx
	p_brands = []  # field = wBrand
	p_manufacturerIds = []  # field = wManufacturerPartNo
	p_supplierIds = []  #  wSupplierId
	p_sources = []  # field = wSource
	p_descriptions = []  # field = wDescription
	p_details = []  # field = wDetails
	p_categories = []  # field = wCategory

	# set api-endpoint and parameters
	URL = "https://api.ince.live/product"
	apikey = '4f032b1a18ab3f36'
	source = 'brammer'

	i = 0
	if test == True:
		search_vals = mMats_test
	else:
		search_vals = mMats
	for code in search_vals:
		if code == '': code = 'null'

		# send get request to api and save the response in a response object
		PARAMS = {'apikey':apikey, 'source':source, 'id':code}
		r = requests.get(url = URL, params = PARAMS)

		try:
			data = r.json()
		except:
			data = 'Server error'
			print('{}: {}'.format(code, 'server error'))
			# print results to pandas col arrays
			p_searchIds.append(code)
			p_brands.append('')
			p_manufacturerIds.append('')
			p_supplierIds.append('')
			p_sources.append('')
			p_descriptions.append('')
			p_details.append('')
			p_categories.append('')
			i += 1
			continue

		# check to see if the api responds to the id request
		try:
			searchId = data[0]['searchID']
		except:
			searchId = 'id not found'

		# if api returns response to the id request,
		# it will return a list, so proceed by parsing
		# the list by looping through it index-wise
		# to retrieve brandStr as brand and descriptionStr as brand:manufacturerID:description
		if searchId != 'id not found':
			# because the api may return multiple dictionaries for a single searchID,
			# we'll collect the results in list containers, and afterward append the lists
			# to the column containers for pandas
			# brand     |  manufacturerID       |  supplierID     |  source     |  description     |  details    |  productCategory
			# wBrand    |  wManufacturerPartNo  |  wSupplierId    |  wSource    |  wDescription    |  wDetails   |  wCategory
			# p_brands  |  p_manufacturerIds    |  p_supplierIds  |  p_sources  |  p_descriptions  |  p_details  |  p_categories
			j = 0
			#brandStr = []
			#descriptionStr = []
			#detailsStr = []
			#categoryStr = []
			#unique_brand = []
			#unique_source = []
			#for index in data:
			# collect results in list containers
			# search id
			p_searchIds.append(code)

			# brand
			p_brands.append(data[j]['brand'])

			# manufacturer part no
			try: manufacturerPartNo = data[j]['manufacturerID']
			except: manufacturerPartNo = ''
			p_manufacturerIds.append(manufacturerPartNo)

			# supplier id
			p_supplierIds.append(data[j]['supplierID'])

			# source
			p_sources.append(data[j]['source'])

			# description
			p_descriptions.append(data[j]['description'])

			# details
			# handle errors where details return a null value
			try: details = data[j]['details']
			except: details = ''
			p_details.append(details)

			# categories
			p_categories.append(data[j]['productCategory'])

			#j += 1

			# print results to console
			# p_brands  |  p_manufacturerIds    |  p_supplierIds  |  p_sources  |  p_descriptions  |  p_details  |  p_categories
			print('{}: {} | {} | {} | {} | {} | {} | {}'.format(
				code, p_brands[i], p_manufacturerIds[i], p_supplierIds[i],
				p_sources[i], p_descriptions[i], p_details[i], p_categories[i]))

			'''
			# print results to pandas col arrays
			p_searchId.append(code)
			p_sources.append(sourceStr)
			p_brands.append(brandStr)
			p_descriptions.append(descriptionStr)
			p_details.append(detailsStr)

			'''
		else:
			# print results to console
			print('{}: empty'.format(code))

			# print results to pandas col arrays
			p_searchIds.append(code)
			p_brands.append('')
			p_manufacturerIds.append('')
			p_supplierIds.append('')
			p_sources.append('')
			p_descriptions.append('')
			p_details.append('')
			p_categories.append('')

		i+= 1
	# end api call  //

	# print contents of pandas arrays to excel file (.xlsx)
	df = pd.DataFrame({'searchId':p_searchIds, 'wBrand':p_brands, 'wManufacturerId':p_manufacturerIds, 'wSupplierId':p_supplierIds, 'wSource':p_sources, 'wDescription':p_descriptions, 'wDetails':p_details, 'wCategory':p_categories})
	writer = pd.ExcelWriter(pdFile)
	df.to_excel(writer,'Product Data', index=False)
	writer.save()

	# end program
	print('Done.')

if __name__ == '__main__': main()
