#!/usr/bin/env python
# coding: utf8
# model trainer test
# Compatible with: spaCy v2.0.0+

'''
Friday, July 5, 2019
Stacy Bridges

Step by step guide (per spaCy documentation):
1.  Load the model you want to use (erp data set).
    If it is an existing model, use nlp.disable_pipes to disable all pipes but NER.
2.  Shuffle and loop over your examples (suppliers & products).
    For each example, use nlp.update to update the model.
    The updater will step through the words of the input. At each word, it will
    make a prediction and then consult the annotations to see if it is correct.
    If not, it will adjust weights to make the correct action score higher next time.
3.  Save the trained model using nlp.to_disk.
4.  Test the model to make sure the entities in the training data are recognized correctly.

For more details, see the documentation:
-   Training: https://spacy.io/usage/training
-   NER: https://spacy.io/usage/linguistic-features#named-entities

'''

# LIB IMPORTS =================================
from __future__ import unicode_literals, print_function
import plac
import random
import sys
import os
import spacy
from spacy.util import minibatch, compounding
from spacy.tokens import Token
from spacy.pipeline import EntityRuler
from pathlib import Path

# IMPORT PATHS ================================
sys.path.append('../../../preprocessor/')

# .PY IMPORTS =================================
#import loader
import string_cleaner

# GLOBALS  ====================================
# training data
# 28 patterns
TRAIN_DATA = [
    ("wrwx ball bearing 6220c3 (preheater) mach=fag",{"entities": [(25-7, 31-7, "MMAT")]}),
    ("wrwx 6002 bearing[manfcode= 6002][manf=skf][mac)",{"entities": [(35-7, 39-7, "MMAT")]}),
    ("wrwx na4920 bearing manfcode na4920 manf fag",{"entities": [(12-7, 18-7, "MMAT")]}),
    ("wrwx 3306a bearing manfcode 3306a manf fag m",{"entities": [(12-7, 17-7, "MMAT")]}),
    ("wrwx ball bearing 6226 9101 fag",{"entities": [(25-7, 29-7, "MMAT")]}),
    ("wrwx ball bearing 1040 x 1.1/2in fag",{"entities": [(25-7, 29-7, "MMAT")]}),
    ("wrwx ball bearing fag ls13ac 5337 (ki",{"entities": [(29-7, 35-7, "MMAT")]}),
    ("wrwx ball bearing 6213 9573 fag",{"entities": [(25-7, 29-7, "MMAT")]}),
    ("wrwx roller bearing 20207 9230 fag or skf",{"entities": [(27-7, 32-7, "MMAT")]}),
    ("wrwx bearing 6202-2rs fag",{"entities": [(20-7, 28-7, "MMAT")]}),
    ("wrwx fag bearing 22214e1",{"entities": [(24-7, 31-7, "MMAT")]}),
    ("wrwx fag bearing ge100 es by fag, radial spherical bearings",{"entities": [(24-7, 29-7, "MMAT")]}),
    ("wrwx timken 61805 deep grove vearings",{"entities": [(19-7, 24-7, "MMAT")]}),
    ("wrwx nsk 524 deep grooves bearing",{"entities": [(16-7, 19-7, "MMAT")]}),
]

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)

# FUNCTIONS  ==================================

# MAIN  =======================================
def main(model=None, output_dir="model_entRuler", n_iter=70):
    # setup pipeline
    # load the model you want to use
    # use nlp.disable_pipes to disable all pipes but NER

    """
    Load the model, set up the pipeline and train the entity recognizer.
    """
    if model is not None:
        nlp = spacy.load('model')  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        #nlp = spacy.load('en_core_web_sm', disable=['tagger', 'parser'])
        print("Created blank 'en' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # ADD EXISTING/TRAINED ENTITY RULER  ----------------
    # load patterns from external file
    #nu_ruler = EntityRuler(nlp).from_disk('iesa_ners_patterns_mmat.jsonl')

    # putting the ruler before ner will override ner decisions in favor of ruler patterns
    #nlp.add_pipe(nu_ruler, before='ner')

    # show pipeline components:
    print(nlp.pipe_names)
    # --------------------------------------------------

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        # reset and initialize the weights randomly – but only if we're
        # training a new model

        if model is None:
            nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            print("Losses", losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # show pipeline components:
    print(nlp.pipe_names)

    # end program
    print('Done.')

if __name__ == '__main__' :
    plac.call(main)
