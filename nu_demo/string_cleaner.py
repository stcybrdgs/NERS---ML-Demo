# -*- coding: utf-8 -*-
"""
Created on Thur Jun 13 14:49:44 2019
@author: Stacy

scripts to perform cleaning operations on a doc and return it to caller

preprocessor/
    string_cleaner.py
    # imports: [ unicodedata2, re ]
        # helper functions
            # def lemmatizer(d)
            def remove_accents(d)
            def remove_special_chars(d)
            def remove_whitespace(d)
            def normalizer(d)
            def apply_custom_rules(d)
            def porter_stemmer(d)
        # controller function
            def string_cleaner(d)

"""
# IMPORT LIBS  =====================================
import unicodedata2
import re
import jellyfish
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from spacy.lang.en.stop_words import STOP_WORDS

# IMPORT PATHS  ====================================

# IMPORT FUNCTIONS  ================================
#import loader

# GLOBALS  =========================================
# define special characters to be removed from doc
# rem keep '/' for cases such as 1/2 kg, etc
# rem keep ':' for skus that need it
# rem keep ',' for numbers that need it
# rem keep '.' for numbers that need it
special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(',
                ')', '{', '}', '[', ']', '|', '\\', ';', '\"',
                '\'', '<', '>', '?', '£', '.', ':', ',', '-', '=']

nlp = spacy.load('en_core_web_sm')

# HELPER FUNCTIONS  =================================
def remove_accents(d):
    # rem unicode is default on python3
    try:
        d = unicode(d, 'utf-8')
    except (TypeError, NameError):
        pass

    d = unicodedata2.normalize('NFC', d)
    d = d.encode('ascii', 'ignore')
    d = d.decode("utf-8")
    return str(d)
    # end function //

def remove_special_chars(d):
    for char in special_chars:
        if d.find(char) >= 0:
            d = d.replace(char, ' ')
    return d
    # end function //

# change all strings to lowercase
def convert_to_lowercase(d):
    d = d.lower()
    return d
    # end function //

def enforce_stop_words(d):
    doc = nlp(d)
    str_doc = ''
    for tok in doc:
        if tok.is_stop == False:
            str_doc = str_doc + tok.text + ' '
    return str_doc
    # end function //

def apply_custom_rules(d):
    # hyphens to colons ----------------------------

    # replace 12-123 pattern with 12:123
    # rem   pos_ of 12-123 returns NUM SYM NUM but
    #       pos_ of 12:123 returns NUM
    #   stuff goes here

    # commas to whitespace if not numerical --------
    # rem replace '1,000, token' with '1,000 token'
    #   stuff goes here
    return d
    # end function //

def remove_whitespace(d):
    d = d.strip()  # remove leading and trailing whitespace
    d = re.sub(' +', ' ', d)  # remove duplicative whitespace
    return d
    # end function //

def lemmatizer(d):
    lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
    doc = nlp(d)
    str_doc = ''
    for tok in doc:
        # rem a lemmatized string is returned as a list
        # so it must be indexed to be 'unpacked' for string comparison
        if tok.text != lemmatizer(tok.text, tok.pos_)[0] and tok.pos_ == 'NOUN':
            #print(tok.text, lemmatizer(tok.text, tok.pos_), tok.pos_, tok.tag_, '\n')
            str_doc = str_doc + str(lemmatizer(tok.text, tok.pos_)[0]) + ' '
        else:
            str_doc = str_doc + tok.text + ' '
    return str_doc
    # end function //

# Reduce the string s to its stem using the common Porter stemmer.
def porter_stemmer(d):
    start = 0
    end = 0
    nu_d = ''
    for char in d:
        if char == ' ':
            #print('Stemming ', s[start:end])
            nu_d = nu_d + jellyfish.porter_stem(d[start:end]) + ' '
            start = end
        end += 1
    d = nu_d
    return d
    # end function //

# CONTROLLER FUNCTION  =============================
def clean_doc(d):
    d = remove_accents(d)
    d = remove_special_chars(d)
    d = convert_to_lowercase(d)
    d = enforce_stop_words(d)
    d = apply_custom_rules(d)
    d = remove_whitespace(d)
    #d = lemmatizer(d)
    #d = porter_stemmer(d)

    return d
    # end function //
