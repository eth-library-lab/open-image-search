#!/usr/bin/env python
# coding: utf-8

# # Train Similarity Search Algorithm
# 
# This notebook trains a model on the previously extracted image features which will search for the most similar image
# 
# 

# In[6]:


import os
import sys
import pandas as pd
import numpy as np
import csv
from sklearn.neighbors import NearestNeighbors
from joblib import dump, load

sys.path.append('../src')
import utils
import settings

def get_feature_extractor_notes(features_serial_num):
    
    fname = 'features_notes_{}.txt'.format(features_serial_num)
    fldr_path = os.path.join('..', 'data','processed')
    fpath = os.path.join(fldr_path, fname)

    with open(fpath,'r') as f:
        features_notes = f.readlines()
    
    return features_notes


def save_model_notes(clf, model_fldr=None):    
    
    if not model_fldr:
        model_fldr = os.path.join('..','models','search', clf.created)

    # write model params to notes file
    fpath = os.path.join(model_fldr, "notes.txt") 

    #get notes about features
    try:
        feature_notes = get_feature_extractor_notes(clf.features_file_serial_num)
    except:
        print("Error: could not load feature notes")
        feature_notes = None

    #write to file
    with open(fpath,'w') as f:

        # write feature extractor notes
        if feature_notes:
            for i, line in enumerate(feature_notes):
                if i==0:
                    line = "Feature_Extraction_" + line
                f.write(line)
        # write search algorithm notes
        f.write("features_file_serial_num: {}\n".format(clf.created))
        f.write("search_algorithm_name: {}\n".format(clf.name))
        for k,v in clf.get_params().items():    
            f.write("{}: {}\n".format(k,v))
    
    print("saved model params to: {}".format(fpath))
    
    return


def save_model_and_notes(clf, model_folder):
    """
    serialize a scikit learn classifier and save to file
    save assosciated classifier notes to the same folder
    """
    # make folder
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    save_model_notes(clf, model_folder)
    
    # serialize (save) model
    fname = '{}.joblib'.format(clf.name)
    fpath = os.path.join(model_folder,fname)
    clf_fpath = dump(clf, fpath)
    clf_fpath = clf_fpath[0]
    
    print("saved model to: {}".format(clf_fpath))
    
    return clf_fpath


def init_and_fit_nearest_neighbours(features_list, 
                                    n_neighbours=10,
                                    algorithm='brute',
                                    metric='euclidean'):

    clf_name = 'NearestNeighbors{}'.format(n_neighbours) 
    clf = NearestNeighbors(n_neighbors=n_neighbours, 
                           algorithm=algorithm, 
                           metric=metric)

    # add additional attributes to model
    timestamp = utils.time_stamp()
    clf.name = clf_name
    clf.created = timestamp

    #fit model
    clf = clf.fit(features_list)
    
    return clf


def main():

    labels, features_list  = utils.load_features(fpath=settings.features_fpath)

    # # Train Classifier
    clf = init_and_fit_nearest_neighbours(features_list, 
                                        n_neighbours=10,
                                        algorithm='brute',
                                        metric='euclidean')

    # Save model
    clf_fpath = save_model_and_notes(clf, settings.search_model_fldr_path)

    return


if __name__ == '__main__':

    main()
