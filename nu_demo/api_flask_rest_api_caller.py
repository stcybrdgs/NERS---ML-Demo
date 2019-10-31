import requests
import csv

# set api-endpoint for local flask rest api
URL = "http://127.0.0.1:5000/product/"

inFile = r'C:\Users\stacy\My GitHub\wxMatchingEngine\store\model\brmr_erp1\nu_demo\out_mmat_pandas.csv'
manuf_ids = []
results = []
hit = 0
miss = 0
with open(inFile) as data:
    csv_reader = csv.reader(data, delimiter='|')
    i = 0
    for row in csv_reader:
        if i > 0:
            if row[0] == '':
                id = 'empty'
            else:
                id = row[0]
            manuf_ids.append(id.replace(" ", "").lower())
            # populate txt obj
            #doc = doc + 'wrwx ' + ('|'.join(row) + '\n')
        i += 1

for manuf_id in manuf_ids:
    # send get request and save response as response object
    #PARAMS = 'Stacy'
    r = requests.get(url = URL + manuf_id)  #, params = PARAMS)

    # extracting data in json format
    data = r.json()

    # Product	Manuf_Id	Manuf	Attributes
    #print(manuf_id)
    #print('Here')
    #print(data['product'], data['manuf_id'], data['manuf'], data['attributes'])
    #print('There')
    try:
        product = data['product']
    except:
        product = 'none'
    try:
        #print('TRY: ', data['manuf_id'].replace(" ", "").lower())
        manuf_id = data['manuf_id']
    except:
        manuf_id = 'none'
    try:
        manuf = data['manuf']
    except:
        manuf = 'none'
    try:
        attributes = data['attributes']
    except:
        attributes = 'none'

    if manuf_id == 'none':
        results.append('Product not found')
        miss += 1
    else:
        results.append({product, manuf, manuf_id, attributes})
        hit += 1


print('\n\nAPI Results --------------------------')
for item in results:
    print(item)
print('\n{} total requests, {} hits, {} missed'.format(hit+miss, hit, miss))

j = 0
for item in manuf_ids:
    j += 1

print(j)
