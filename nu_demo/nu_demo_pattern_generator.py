#!/usr/bin/env python
# coding: utf8
# Compatible with: spaCy v2.0.0+
'''
Sunday, July 19, 2019
Stacy Bridges

'''
# IMPORT LIBS  =================================
import spacy
import csv

# MAIN  ========================================
def main():
    # set parameters to run either MMAT or MANUF (only one choice per run)
    dataLabel = 'MMAT'  # MMAT or MANUF

    if dataLabel == 'MMAT':
        dataIn = 'in_mmat.csv'  # in_mmat.csv or in_manuf.csv
        dataOut = 'out_mmat_patterns.jsonl'  # out_mmat.jsonl or out_manuf.jsonl
    elif dataLabel == 'MANUF':
        dataIn = 'in_manuf.csv'  # in_mmat.csv or in_manuf.csv
        dataOut = 'out_manuf_patterns.jsonl'  # out_mmat.jsonl or out_manuf.jsonl

    # declare containers
    patterns = []

    # parameters
    infile  = 'C:/Users/stacy/My GitHub/wxMatchingEngine/store/model/brmr_erp1/nu_demo/' + dataIn
    outfile = 'C:/Users/stacy/My GitHub/wxMatchingEngine/store/model/brmr_erp1/nu_demo/' + dataOut

    # import erp csv
    doc = ''
    with open(infile) as data:
        csv_reader = csv.reader(data, delimiter = '|')
        i = 0
        for line in csv_reader:
            if i > 0:  # skip header row
                # populate patterns
                pattern = ''
                prefix = '{"label":"' + dataLabel + '", "pattern":[{"lower":"'
                inner = ''
                suffix = '"}]}'
                for char in line:
                    if char == ' ':
                        inner = inner + '"},{"lower":"'
                    else:
                        inner = inner + char.lower()
                pattern = prefix + inner + suffix + '\n'

                # detect duplicates and append only unique patterns
                # to the patterns list
                pattern_exists = False
                for p in patterns:
                    if p == pattern:
                        pattern_exists = True
                if not pattern_exists:
                    patterns.append(pattern)
            i += 1

    # create pattern files using jsonl
    # supplier patterns:
    with open(outfile, 'w') as outfile:
        for line in patterns:
            outfile.write(line)
            print(line)

    # end program
    print('Done.')

if __name__ == '__main__' : main()
