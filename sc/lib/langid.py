""" Load and configure the langid library """


import gzip
import pickle
import pathlib

import sc
from langid import langid
# Free up a couple mb of ram
del langid.model


def rank(string):
    return identifier.rank(string)

def load_model():
    # code copied from LanguageIdentifier.from_modelstring
    global identifier
    
    modelpath = pathlib.Path(__file__).parent / './langid.model.gz'
    
    import gzip
    with gzip.open(str(modelpath), 'rb') as f:
        model = pickle.load(f)
    
    import numpy as np
    
    nb_ptc, nb_pc, nb_classes, tk_nextmove, tk_output = model
    nb_numfeats = len(nb_ptc) / len(nb_pc)

    # reconstruct pc and ptc
    nb_pc = np.array(nb_pc)
    nb_ptc = np.array(nb_ptc).reshape(len(nb_ptc)/len(nb_pc), len(nb_pc))
   
    return langid.LanguageIdentifier(nb_ptc, nb_pc, nb_numfeats, nb_classes, tk_nextmove, tk_output)


identifier = load_model()
