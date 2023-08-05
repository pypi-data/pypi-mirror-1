#!/usr/bin/python

###############################################################################
# NAME: pypedal.py
# VERSION: 0.10 (5JUNE2002)
# AUTHOR: John B. Cole (jcole@lsu.edu)
# LICENSE: LGPL
###############################################################################

from pyp_classes import *
from pyp_io import *
from pyp_metrics import *
from pyp_nrm import *
from pyp_utils import *

if __name__=='__main__':

    print 'Starting pypedal.py at %s' % asctime(localtime(time()))
    print '\tPreprocessing pedigree at %s' % asctime(localtime(time()))
    example = preprocess('example.ped')
    print '\tCalling fast_a_matrix() at %s' % asctime(localtime(time()))
    ex_a = fast_a_matrix(example,'example')
    #print '\tCalling a_decompose() at %s' % asctime(localtime(time()))
    #de_a_t,de_a_d = a_decompose(example,'example',ex_a)
    #print '\tCalling a_inverse_dnf() at %s' % asctime(localtime(time()))
    #my_ainv_dnf = a_inverse_dnf(example,'example')
    #print '\tCalling a_inverse_df() at %s' % asctime(localtime(time()))
    #my_ainv_df = a_inverse_df(example,'example')
    print '\tCalling a_coefficients() at %s' % asctime(localtime(time()))
    a_coefficients(example,'example',ex_a)
    #print '\tCalling a_effective_founders_lacy() at %s' % asctime(localtime(time()))
    #a_effective_founders_lacy(example,'example')
    #print '\tCalling a_effective_founders_boichard() at %s' % asctime(localtime(time()))
    #a_effective_founders_boichard(example,'example')
    #print '\tCalling a_effective_ancestors_boichard() at %s' % asctime(localtime(time()))
    #try:
    #    a_effective_ancestors_definite(example,'example')
    #except:
    #    print '\tERROR in a_effective_ancestors_boichard() at %s' % asctime(localtime(time()))
    # Instantiate a pedigree metadata object
    example_meta = Pedigree(example,'example.ped','example_meta')
    try:
        theoretical_ne_from_metadata(example_meta,filetag='example')
    except:
       print '\tERROR in theoretical_ne_from_metadata() at %s' % asctime(localtime(time()))
       pass
    try:
        print '\tCalling pedigree_completeness() at %s' % asctime(localtime(time()))
        pedigree_completeness(example,filetag='example')
    except:
       print '\tERROR in pedigree_completeness() at %s' % asctime(localtime(time()))
       pass
       
    print 'Stopping pypedal.py at %s' % asctime(localtime(time()))
