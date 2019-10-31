# -*- coding: utf-8 -*-
'''
Wenesday July 17, 2019
Stacy Bridges

bearing decoder
- this script makes GET request from SKF API using mMatIDs

mMat  |  shortDescription  |  longDescription  |  Attributes[]

'''
# IMPORTS  ---------------------------------------------------------
import csv
import requests

# GLOBALS  ---------------------------------------------------------
row_heads = ['SBT_Code', 'Bearing Type', 'Bearing Attributes']
mMats = []

# FUNCTIONS  -------------------------------------------------------
def import_csv(d):
	doc = ''
	code = ''
	with open(d) as data:
		csv_reader = csv.reader(data, delimiter='|')
		i = 0
		for row in csv_reader:
			if i > 0:
				# populate txt obj
				doc = doc + ('|'.join(row) + '\n')
				code = row
				mMats.append(code)
			i += 1
	return doc
    # end function //

# MAIN  ------------------------------------------------------------
def main():
	#exception = False
	rows_for_csv = []  # each index contains a row that will be written to the csv
	attr_str =''  # use to collect api text that will be inserted into attributes[]
	row_str = ''  # use to collect api text that will be inserted into rows_for_csv[]
	counter = 0   # control counter for intermittent writes to external file

	# declare input/output files
	inFile = r'C:\Users\stacy\My GitHub\wxMatchingEngine\store\model\brmr_erp1\nu_demo\out_mmat_pandas.csv'
	outFile = 'C:/Users/stacy/My GitHub/wxMatchingEngine/store/model/brmr_erp1/nu_demo/api_bearing_decoder_output.csv'

	with open(outFile, 'w') as writeFile:
		writer = csv.writer(writeFile)

		# populate headers for csv file
		global row_heads
		i = 0
		for row in row_heads:
			if i == 0:
				row_str = row_str + row_heads[i]
			else:
				row_str = row_str + '|' + row_heads[i]
			i += 1
		rows_for_csv.append([row_str])
		print(row_str, '---------')
		row_str = ''

		# get codes as doc obj from external file
		input_file = inFile  # 'bearing_decoder_input.csv'
		codes = import_csv(input_file)

		# set api-endpoint for SKF
		URL = "https://search.skf.com/prod/search-skfcom/rest/apps/site_search/searchers/products"
		#https://search.skf.com/prod/search-skfcom/rest/apps/site_search/searchers/products?q=6003

		i = 0
		for code in mMats:
			# sending get request and saving the response as response object
			if len(code) == 0:
				row_str = 'empty code: result not found'
			else:
				PARAMS = {'q':code}
				r = requests.get(url = URL, params = PARAMS)

				# extracting data in json format
				data = r.json()

				# get description (ie, designation and category)
				try:
					designation = data['documentList']['documents'][0]['designation']
				except:
					designation = 'code not found'
					#exception = True
				try:
					category = data['documentList']['documents'][0]['category']
				except:
					category = 'Bearing type not found'

				# add them to the csv string
				row_str = row_str + designation + '|' + category + '|'


				#if exception == False:
				# get bearing attributes
				try:
					search_result = data['documentList']['documents'][0]['search_result_nested']
				except:
					search_result = ''

				j = 0
				for item in search_result:
					try:
						name = search_result[j]['name']
					except:
						name = 'name not found'
					try:
						value = search_result[j]['value']
					except:
						value = 'value not found'
					try:
						unit = search_result[j]['unit']
					except:
						unit = 'unit not found'

					if j > 0:
						attr_str = attr_str + ', '
					attr_str = attr_str + name + ': ' + str(value) + ' ' + unit
					j += 1

				# add the attributes to the csv string
				row_str = row_str + attr_str

			print(row_str)

			# store the string in a list so that it can be added to the csv
			rows_for_csv.append([row_str])

			# reset strings
			row_str = ''
			attr_str = ''
			#exception = False

			counter += 1
			if counter == 500:
				# write data to csv file
				writer.writerows(rows_for_csv)
				counter = 0
				rows_for_csv.clear()

			i+= 1

		# write data to csv file
		writer.writerows(rows_for_csv)

	# end program
	print('Done.')

if __name__ == '__main__': main()
