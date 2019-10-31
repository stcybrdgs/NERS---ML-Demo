import csv
import requests
import pandas as pd
from pandas import ExcelWriter
import numpy as np

# hardcoded id inputs
# specify array of ids (use quotes to comment out if using external id inputs)
id_array = ['6001', '6004', '607', '6003-2Z-C3', '6003-2Z/C3']

print(', '.join(id_array))

if '608' not in id_array:
    print('it is not here')

print('array has:', id_array)
id_array = []
print('array has:', id_array)

df = id_array
pd.DataFrame(df)

print('Done')
