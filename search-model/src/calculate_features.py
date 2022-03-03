#!/usr/bin/env python
# coding: utf-8

# # Calculate Features
# 
# this script uses a CNN to extract features from the images in the directory. 
# The results are saved to a csv.

import tensorflow as tf
import os, sys
import csv
import pandas as pd
import numpy as np
from datetime import datetime as dt

import utils
import utils_tf
import settings

def initialise_model_vgg16(print_summary=True, model_name='vgg16_imagenet', weights='imagenet'):
    """initialise the model to be used for feature extraction"""
    
    model_backbone = tf.keras.applications.VGG16(include_top=False, weights=weights, input_shape=(224,224,3))
    backbone_output = model_backbone.layers[-1].output # drop the last max pooling layer from vgg
    
    pooling_lyr = tf.keras.layers.MaxPool2D(pool_size=(7,7))(backbone_output)
    flatten_lyr = tf.keras.layers.Flatten()(pooling_lyr)
    norm_lyr = tf.keras.layers.LayerNormalization()(flatten_lyr)
    model = tf.keras.Model(inputs=model_backbone.inputs, outputs=norm_lyr)

    if model_name:
        model._name = model_name

    if print_summary==True:
        print(model.summary())
    
    return model


def save_feature_extractor_notes(fldr_path, model, weights):
    """
    """
    # save model summary    
    fname = 'feature_extractor_notes.txt'
    fpath = os.path.join(fldr_path, fname)
    utils.prep_dir(fpath)

    with open(fpath,'w') as f:
        f.write("Model Name: {} \n".format(model.name))
        f.write("Model weights: {} \n".format(str(weights)))
        # Pass the file handle in as a lambda function to make it callable
        model.summary(print_fn=lambda x: f.write(x + '\n'))


def make_empty_features_csv(fpath):
    """
    creates an empty csv file to hold extracted features
    returns fpath to the file
    """

    # save empty csv to hold features
    with open(fpath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

    print('outputting features to: ', fpath)

    return fpath


def append_tf_features_to_csv(features, labels, fpath):
    """
    convert tensorflow features and labels to numpy arrays and append
    them to an existing csv
    """
    #make sure labels are stings. e.g.: convert bytes to strings
    labels_column = np.expand_dims(labels.numpy().astype(str), axis=1)
    lab_feat_arr = np.hstack((labels_column, features))

    with open(fpath, 'a', newline='') as csvfile:
        np.savetxt(csvfile, lab_feat_arr, delimiter=',', fmt='%s')

    return    


def calculate_total_steps(num_images, batch_size):
    """calculate the number of steps needed to run all images through model"""
    total_steps = int(np.ceil(num_images / batch_size))

    return total_steps


def print_startup_statuses(num_images, total_steps, output_fpath):
    """print some info to console about process about to run"""

    print('starting feature extraction for:')
    print('    {:,} images in {:,} steps'.format(num_images, total_steps))
    print('    writing features to {}'.format(output_fpath))

    return  


def print_settings(sttngs):
    print("BASE_DIR: ", sttngs.BASE_DIR)
    print(sttngs.model_fldr_path)


def main():
    
    print_settings(settings)
    features_output_fldr_path = os.path.dirname(settings.interim_features_fpath)

    preprocessed_image_dir = settings.processed_image_dir
    input_image_csv = None

    # load csv and make tensorflow dataset
    if input_image_csv:
        print('using files listed in csv: ', input_image_csv)
        df = pd.read_csv(input_image_csv, index_col=0)
        filepath_col_name=settings.filepath_col_name
        label_col_name=settings.label_col_name

    elif preprocessed_image_dir:
        print('using files in directory: ', preprocessed_image_dir)
        df = utils.make_df_file_list(preprocessed_image_dir)
        filepath_col_name='file_path'
        label_col_name='identifier'

        df[label_col_name] = df[filepath_col_name].apply(
            lambda fpath: os.path.basename(fpath).rsplit(".",maxsplit=1)[0]
        )

    num_images = df.shape[0]    

    ds = utils_tf.make_tfdataset_from_df(df, 
                            filepath_col_name,
                            label_col_name,
                            batch_size=settings.batch_size,
                            for_training=False,
                            normalize=False,
                            augment=False,
                            augment_func=None,
                            conv_color='rgb')

    # load the model
    model = initialise_model_vgg16(print_summary=False, 
                                model_name=settings.model_name,
                                weights=settings.weights)
    model.compile()
    
    # save the model that will be used for feature extraction
    if not os.path.exists(settings.model_fldr_path):
        os.makedirs(settings.model_fldr_path)
        model.save(settings.model_fldr_path, save_format='tf')

    #save model summary text file in the features file folder
    save_feature_extractor_notes(features_output_fldr_path, model, settings.weights)
    
    # make an output csv file to store the features in
    exists = os.path.exists(settings.interim_features_fpath) == True
    if exists:
        overwrite = utils.overwrite_if_exists(settings.interim_features_fpath)
        if overwrite == False:
            print("skipping feature extraction")
            return
        else: 
            output_fpath = make_empty_features_csv(settings.interim_features_fpath)
    else: 
        output_fpath = make_empty_features_csv(settings.interim_features_fpath)
    # print start up statuses
    total_steps = calculate_total_steps(num_images, settings.batch_size)
    print_startup_statuses(num_images, total_steps, output_fpath)

    for i, (images, labels) in enumerate(iter(ds)):
        #extract features
        features = model.predict(images)
        append_tf_features_to_csv(features, labels, output_fpath)
        #update progress bar
        utils.print_dyn_progress_bar(total_steps,i)

    print("\n")
    return

if __name__ == '__main__':

    main()