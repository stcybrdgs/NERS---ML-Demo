#!/usr/bin/env python
# coding: utf8
# Compatible with: spaCy v2.0.0+

# IMPORTS  =====================================
import os
import sys
import spacy
from spacy import displacy
import csv
from spacy.pipeline import EntityRuler
from spacy.pipeline import Tagger
from spacy.language import Language
from pathlib import Path
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from spacy.lang.en.stop_words import STOP_WORDS
import json
import pandas as pd
from pandas import ExcelWriter
import numpy as np
#from spacy.lang.en import English

# PATHS  =======================================
sys.path.append('../../../preprocessor')

# IMPORT PY FILES  =============================
import string_cleaner

# GLOBALS  =====================================
global row_heads
row_heads = []

# FUNCTIONS  ===================================
def sentence_segmenter(doc):
    for token in doc:
        if token.text == 'wrwx':
            doc[token.i].is_sent_start = True
    return doc
    # end function //

def import_csv(d):
    global row_heads
    doc = ''
    with open(d) as data:
        csv_reader = csv.reader(data, delimiter='|')
        i = 0
        for row in csv_reader:
            # populate row_heads[]
            #if i > 0:  # skip header row
            row_head = row[0]
            row_heads.append(row_head)
            # populate txt obj
            doc = doc + 'wrwx ' + ('|'.join(row) + '\n')
            i += 1
    return doc
    # end function //

def stemmer(d):
    pass

def entRuler_tagger(doc):
   # do something to the doc here
   pass

def update_meta_pipeline():
    pass

def combine_pattern_files(mmats, manufs):
    outFile = r'C:\Users\stacy\My GitHub\wxMatchingEngine\store\model\brmr_erp1\nu_demo\out_mmat_manuf_patterns.jsonl'
    #print(outFile)
    of = open(outFile, 'wt')
    mmatFile = open (mmats, 'rt')
    manufFile = open(manufs, 'rt')
    for line in mmatFile:
        of.writelines(line)
        #print('.', end='', flush=True) # rem flush the output buffer
    for line in manufFile:
        of.writelines(line)
        #print('.', end='', flush=True) # rem flush the output buffer
    mmatFile.close()
    manufFile.close()
    of.close()

    return outFile

# MAIN  ========================================
def main():
    '''
    NERS Demo w/ Sample Data
    '''
    # CONFIG  ---------------------- \\
    # -------------------------------- \\
    model = 'post'   # pre -> use non-trained model / post -> use trained model
    mmat = 'on'  # on/off
    manuf = 'on'  # on/off
    ruler = 'on'
    cleaner = 'on'
    number_tagger = 'off'

    # rem if stemmer is turned on after model does P2 training, then
    # you will need to use POS tag to detect nouns in products
    # then create new generator patterns for all.json
    # then run entity ruler again
    stemmer = 'off'

    # declare inputs / outputs
    mmat_pandas_file = r'C:\Users\stacy\My GitHub\wxMatchingEngine\store\model\brmr_erp1\nu_demo\out_mmat_pandas.xlsx'  # output
    mmat_file = r'C:\Users\stacy\My GitHub\wxMatchingEngine\store\model\brmr_erp1\nu_demo\out_mmat_patterns.jsonl'  # input
    manuf_file = r'C:\Users\stacy\My GitHub\wxMatchingEngine\store\model\brmr_erp1\nu_demo\out_manuf_patterns.jsonl'  # input

    if mmat == 'off' and manuf == 'off':
        patterns_file = mmat_file
    if mmat == 'on' and manuf == 'off':
        patterns_file = mmat_file
    elif mmat == 'off' and manuf == 'on':
        patterns_file = manuf_file
    elif mmat == 'on' and manuf == 'on':
        patterns_file = combine_pattern_files(mmat_file, manuf_file)

    tender_file = r'C:\Users\stacy\My GitHub\wxMatchingEngine\store\model\brmr_erp1\nu_demo\in_tender_short.csv'
    #output_file = 'demo_ners_output_nonstock.txt'
    write_type = 'w'

    # -------------------------------- //
    # ------------------------------ //

    # load model
    if model == 'pre':
        # load a language and invoke the entity ruler
        nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner']) #('en_core_web_sm', disable=['parser'])
    elif model == 'post':
        nlp = spacy.load('model_entRuler')

    nlp.add_pipe(sentence_segmenter, after='tagger')

    # add pipes
    if ruler == 'on':
        # rem if model is post then the entity ruler is already in the model
        if model == 'pre':
            # load patterns from external file only if model is not already trained
            nu_ruler = EntityRuler(nlp).from_disk(patterns_file)
            # putting the ruler before ner will override ner decisions in favor of ruler patterns
            nlp.add_pipe(nu_ruler)#, before='ner')
        # remember to swap precedence between ruler and ner after model training
        if model == 'post':
            # load patterns from external file only if model is not already trained
            if "entity_ruler" not in nlp.pipe_names:
                nu_ruler = EntityRuler(nlp).from_disk(patterns_file)
                # putting the ner before ruler will override favor ner decisions
                nlp.add_pipe(nu_ruler)#, before='ner')

    # show pipeline components:
    print(nlp.pipe_names)

    # import test tender and clean it up
    tender = import_csv(tender_file)  # import
    if cleaner == 'on':
        tender = string_cleaner.clean_doc(tender)  #  clean

    doc = nlp(tender)

    # CONSOLE OUTPUT  ---------------------------------------------------------
    if mmat == 'on' and manuf == 'off':
        print('\n')
        labels = ['MMAT']  # , 'PRODUCT', 'MPN', 'SKU']
        alt_labels = ['Mmat']  # , 'Product', 'MfrPartNo', 'SkuID']
        total_found = []
        total_unique_found = []
        for label in labels:
            print('Results for {} --------------'.format(label))
            tot_num = 0
            unique_num = 0
            unique = []
            for ent in doc.ents:
                if ent.label_ == label:
                    if ent.text not in unique:
                        unique.append(ent.text)
                        unique_num += 1
                    print([ent.text, ent.label_], end='')
                    tot_num += 1
            print('\nFound {} total, {} unique.\n'.format(tot_num, unique_num))
            total_found.append(tot_num)
            total_unique_found.append(unique_num)

    if mmat == 'off' and manuf == 'on':
        print('\n')
        labels = ['MANUF']  # , 'PRODUCT', 'MPN', 'SKU']
        alt_labels = ['Manuf']  # , 'Product', 'MfrPartNo', 'SkuID']
        total_found = []
        total_unique_found = []
        for label in labels:
            print('Results for {} --------------'.format(label))
            tot_num = 0
            unique_num = 0
            unique = []
            for ent in doc.ents:
                if ent.label_ == label:
                    if ent.text not in unique:
                        unique.append(ent.text)
                        unique_num += 1
                    print([ent.text, ent.label_], end='')
                    tot_num += 1
            print('\nFound {} total, {} unique.\n'.format(tot_num, unique_num))
            total_found.append(tot_num)
            total_unique_found.append(unique_num)

    if mmat == 'on' and manuf == 'on':
        print('\n')
        labels = ['MANUF', 'MMAT']  # , 'PRODUCT', 'MPN', 'SKU']
        alt_labels = ['Manuf', 'Mmat']  # , 'Product', 'MfrPartNo', 'SkuID']
        total_found = []
        total_unique_found = []
        for label in labels:
            print('Results for {} --------------'.format(label))
            tot_num = 0
            unique_num = 0
            unique = []
            for ent in doc.ents:
                if ent.label_ == label:
                    if ent.text not in unique:
                        unique.append(ent.text)
                        unique_num += 1
                    print([ent.text, ent.label_], end='')
                    tot_num += 1
            print('\nFound {} total, {} unique.\n'.format(tot_num, unique_num))
            total_found.append(tot_num)
            total_unique_found.append(unique_num)

    # pandas output for mmats  ------------------------------------------------
    # This technique allows you to isolate entities on
    # a sentence-by-sentence basis, which will allow
    # for matching entities on a record-by-record basis
    if mmat == 'on':
        w_MmatCodes = []
        w_MmatCode_Alts = []
        unique = []
        mmat = ''
        alts = ''
        #ent_exists = False
        j = 0
        for sent in doc.sents:
            i = 0
            for ent in sent.ents:
                # ignore header record
                if j > 0:
                    if ent.label_ == 'MMAT':
                        if i == 0:
                            # if it's the first label in the record, save it in mmats
                            mmat = ent.text
                            unique.append(ent.text)
                            i += 1
                        else:
                            # if it's not the first label in the sentence, put it in mmat alts
                            # (if it is already in alts, don't put it in)
                            if ent.text not in unique:
                                unique.append(ent.text)
                                if alts == '':
                                    alts = ent.text
                                else:
                                    alts = alts + ', ' + ent.text
                        #print(ent.label_, ': ', ent.text)

            # store ent results for each record, ignoring the headers
            if j > 0:
                w_MmatCodes.append(mmat.upper())
                w_MmatCode_Alts.append(alts.upper())

                # test ---------------
                print('str ', j, 'w_MmatCodes: ', w_MmatCodes)
                print('str ', j, 'w_MmatCode_Alts: ', w_MmatCode_Alts)
                # test ---------------

            # reset vars for next record
            unique.clear()
            mmat = ''
            alts = ''
            j += 1

        df = pd.DataFrame({ 'w_MmatCodes':w_MmatCodes,
                            'w_MmatCode_Alts':w_MmatCode_Alts})

        writer = pd.ExcelWriter(mmat_pandas_file)
        df.to_excel(writer,'NERS_MMATs', index=False)
        writer.save()

    # save the model  --------------------------------------------------------
    # save model with entity pattern updates made by the entity ruler
    if ruler == "on":
        output_dir = Path('model_entRuler')
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

    # TEST  -----------------------------
    mmats = []

    # DISPLACY VISUALIZER -----------------------------------------------------
    # get results for html doc
    results = ''
    i = 0
    for item in alt_labels:
        results = results + '{}: {} tot  {} unq\n'.format(item, total_found[i], total_unique_found[i])
        i += 1
    # store nlp object as string in html var
    spacer = '---------------------------------------------------------\n'
    header = 'Named Entities Found in Tender\n'
    doc = nlp(header + spacer + results + spacer + tender)

    colors = {
        "MMAT": "#C3FFA1",
        "MANUF": "#FFDDA1",
    }
    options = {"ents": ["MMAT", "MANUF"], "colors": colors}
    # displacy.serve(doc, style="ent", options=options)
    html = displacy.render(doc, style="ent", page=True, options=options)  # use the entity visualizer
    # write the html string to the xampp folder and launch in browser through localhost port
    with open('C:/Users/stacy/My Localhost/index.html', 'w') as data:
        data.write(html)

    print('\n' + results)

    # end program
    print('Done.')

if __name__ == '__main__' : main()
