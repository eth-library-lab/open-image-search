#!/usr/bin/env python
# coding: utf-8

# # Reverse-Image Search for Graphische Sammlung

# image size options   
# 150x150 default  
# 250x250 resolution=mediumImageResolution  
# 350x350 resolution=highImageResolution  
# max resolution=superImageResolution  
# 
# 

# example_url = "https://www.e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=2562&resolution=mediumImageResolution"

# # Image Downloading

import random
import os, sys
import pandas as pd
import numpy as np
from time import sleep
import logging

import utils
import settings

def set_folder(string):
# divide into folders of 999 pictures max

    if len(string)>3:

        fldr = string[0:-3]
    else:
        fldr = "0"

    return fldr


def change_img_url_resolution(url, new_resolution="highImageResolution"):
    
    split_str = '&resolution='
    new_resolution = "highImageResolution"
    
    return url.split(split_str)[0] + split_str + new_resolution
            

def make_dict_from_series(ser_a, ser_b):

    # make dict of filename:url
    ser_a_lst = ser_a.to_list()
    ser_b_lst = ser_b.to_list()
    ser_dict = dict(zip( ser_a_lst, ser_b_lst))

    return ser_dict


def random_sleep_range(sleep_time_range=(1,3)):
    sleep_time = random.uniform(*sleep_time_range)
    sleep(sleep_time)
    return


def save_images(file_dict, sleep_time_range=(3,5)):
 
    """loops through a dictionary of files to download. includes logging
    file_dict: should be in the format {file_fullpath:url }
    """
     
    total_num_images = len(file_dict)
    msg = f"started download of {total_num_images} images"
    print(msg)
    logging.info(msg)

    #loop to download from each url
    for i, (filepath, url) in enumerate(file_dict.items()):

        utils.log_status_at_interval(i, total_num_images, interval=100, _log=True, _print=False)

        # download image
        if not os.path.exists(filepath):
            #make subfolders in file path if doesn't exist
            utils.prep_dir(filepath)
            utils.download_image(filepath, url)
        else:
            logging.warning('image already exists {}'.format(filepath))

        random_sleep_range(sleep_time_range)
        utils.print_dyn_progress_bar(total_num_images, i)

    logging.info('finished download')
    print('\nfinished download')

    return


def filter_existing_files(df, fldr_path, fpath_col='filepath'):
    
    existing_flist = utils.list_files_in_dir(fldr_path)

    for dirpath, dirnames, filenames in os.walk(fldr_path):
        for fname in filenames:
            cur_fpath = os.path.join(dirpath,fname)
            existing_flist.append(cur_fpath)

    orig_len = df.shape[0]

    # filter out already existing
    fltr = ~df[fpath_col].isin(existing_flist)
    df = df.loc[fltr, :]

    num_dropped = orig_len - df.shape[0]
    print('removed {} records with images already saved'.format(num_dropped))
    
    return df


def make_fpaths_col(ser_obj_ids, output_dir):
    
    ser_fpaths = ser_obj_ids.apply(set_folder)
    ser_fpaths = output_dir + '/' + ser_fpaths + '/' + ser_obj_ids + ".png"
    
    return ser_fpaths.apply(os.path.normpath)


def prep_download_df(df, output_dir):
    
    df['id'] = df['id'].astype(int).astype(str)

    # make filepath column
    df['filepath'] = make_fpaths_col(df['id'], output_dir)

    # drop already downloaded records
    df = filter_existing_files(df, output_dir)

    # change image url to lower res
    df.loc[:,'image_url'] = df['image_url'].apply(change_img_url_resolution)

    return df

def main():
    
    # cleaned csv with list of image_ids
    fpath = os.path.join(settings.interim_metadata_dir, 'metadata.csv')
    output_dir = settings.raw_image_dir

    # def main(fpath, output_dir, )
    df = pd.read_csv(fpath, usecols=['id','image_url'])
    df = prep_download_df(df, output_dir)
    img_dict = make_dict_from_series(df['filepath'], df['image_url'])

    utils.init_logging()

    save_images(img_dict, sleep_time_range=(1,2))
    
    return df


if __name__ == '__main__':

    main()