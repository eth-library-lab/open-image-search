# util functions that do not require tensorflow

import os
import numpy as np
import pandas as pd
from PIL import Image
from typing import List, Optional, Text, Tuple
from datetime import datetime as dt
import csv
import logging
import urllib
from io import BytesIO
import re


def make_fpath_from_id(_id, image_fldr="../data/processed/ethz/images"):
    
    res_id = str(_id)

    subfldr = "0"
    if len(res_id)> 3:
        subfldr = res_id[:-3]

    return f"{image_fldr}/{subfldr}/{res_id}.jpeg"

    
def overwrite_if_exists(fpath):
    # make sure the file does already exist before calling this function    

    if os.path.exists(fpath):
        print(f"\nfound existing file: {fpath}")
        user_input = input("Overwrite this file? (Yes / n)")
        return user_input=="Yes"
    
    return True

def is_snake_case(test_string):
    """
    test if a string is in 'snake_case'
    """
    ptrn = "(^[a-z])([a-z0-9]+_?[a-z0-9]?)+([a-z0-9]$)"
    res = re.search(ptrn, test_string)
    return bool(res)


def init_logging(log_fpath=None):

    log_format = (
        '[%(asctime)s] %(levelname)-4s %(name)-8s %(message)s')

    if log_fpath==None:
        log_fpath = '../logs/downloads.log'
    
    prep_dir(log_fpath)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        filename=(log_fpath))
    
    return


def drop_nans_and_duplicates(df):
    rows_input = df.shape[0]

    # drop NaN's
    fltr = df.isna().any(axis=1)
    df = df.loc[~fltr,:]
    # drop duplicates
    df = df.drop_duplicates()

    rows_dropped = rows_input -  df.shape[0]

    print(f"dropped {rows_dropped} due NaN's or duplicates")
    
    return df




def prep_dir(fpath):
    """
    check if the folders in the fpath path exist.
    create them is not
    """
    
    dir_path = os.path.dirname(fpath) 

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return fpath


def log_status_at_interval(i, total_steps, interval=100, _log=True, _print=False):
    #print intermittent milestones to console & log
    if i % interval == 0:
        percent_complete = i/total_steps
        msg = 'currently processing {} of {} ({:0.1%} complete)'.format(i, total_steps, percent_complete)

        if _log:
            logging.info(msg)
        if _print:
            print(msg)


def list_files_in_dir(fldr_path):
    """
    return a list of filepaths for all filers in a give directory
    fldr_path: string, relative path to folder
    """
    existing_flist = []

    for dirpath, dirnames, filenames in os.walk(fldr_path):
        for fname in filenames:
            cur_fpath = os.path.join(dirpath, fname)
            existing_flist.append(cur_fpath)
    
    return existing_flist


def download_image(filepath, url):

    """ requests image from given url and saves it in original quality as jpeg in RGB format
    
    filename: local filepath to save the image to
    url: url to request image from"""
    
    if os.path.exists(filepath):
        logging.info('Image %s already exists. Skipping download.' % filepath)
        return

    try:
        response = urllib.request.urlopen(url)
    except:
        logging.warning('Warning: Could not download image %s from %s' % (filepath, url))
        return

    try:
        pil_image = Image.open(BytesIO(response.read()))
    except:
        logging.warning('Warning: Failed to parse image %s' % filepath)
        return

    try:
        pil_image_rgb = pil_image.convert('RGB')
    except:
        logging.warning('Warning: Failed to convert image %s to RGB' % filepath)
        return

    try:
        pil_image_rgb.save(filepath, format='JPEG')  # , quality=95
    except:
        logging.warning('Warning: Failed to save image %s' % filepath)
        return

      

def time_stamp():
    return dt.now().strftime('%Y%m%d%H%M')


def get_list_of_files_in_dir(fldr_path, file_types = ['jpg', 'jpeg','png'], keep_fldr_path=True):
    """
    file_types: 'all' or list of allowed file endings
    keep_fldr_path: boolean, if false the input fldr_path prefix will be removed from the returned list entries
    """

    existing_flist = []

    for dirpath, dirnames, filenames in os.walk(fldr_path):
        for fname in filenames:
            cur_fpath = os.path.join(dirpath,fname)
            
            if keep_fldr_path == False:
                cur_fpath = cur_fpath.replace(fldr_path, '').strip('/').strip('\\')
            
            if file_types == 'all':
                existing_flist.append(cur_fpath)
            elif (fname.rsplit(".",maxsplit=1)[-1].lower() in file_types) and ('.ipynb_checkpoints' not in cur_fpath):
                existing_flist.append(cur_fpath)
    
    print("{:,} files found in directory".format(len(existing_flist)))
    
    return existing_flist
    

def make_df_file_list(input_image_dir, keep_full_path=False, use_relative_path=True):

    if use_relative_path:
        rel_path = os.path.relpath(input_image_dir, start = os.curdir)
        rel_path += '/'         
        keep_full_path=False

    else:
        rel_path=''

    lst_fpaths = get_list_of_files_in_dir(input_image_dir, 
                                          file_types = ['jpg', 'jpeg','png'], 
                                          keep_fldr_path=keep_full_path )


    df = pd.DataFrame({'file_path':lst_fpaths})
    df['file_path'] = rel_path + df['file_path']

    return df


def print_dyn_progress_bar(total, i):
    """print a progress bar in a single line to monitor a for loop """
    
    barwidth = 50

    percent_complete = (i+1)/total
    completed = int(percent_complete * barwidth)
    remaining = barwidth - completed 
    
    bar_str = "\r[{}{}{}] {:0.2%}".format('-'*completed,
                                          '>',
                                          ' '*remaining,
                                          percent_complete )
    print(bar_str, end='')   
    
    return


def load_features(fpath):
    """
    load the csv of image features calculated by the tf model  
    """
    
    
    with open(fpath,'r') as dest_f:
        data_reader = csv.reader(dest_f,
                               delimiter = ',')
        #next(data_reader) #skips the header/first line
        data = [data for data in data_reader]

    data_array = np.asarray(data)
    labels = data_array[:,0].astype(str)
    features_list = data_array[:,1:].astype(np.float32).tolist()

    return labels, features_list 


def move_file(orig_fpath, new_fpath):

    try:
        utils.prep_dir(new_fpath)
        shutil.move(orig_fpath, new_fpath)
    except Error as e:
        print("could not move: ", orig_fpath, "\n", e)
        
    return


def get_file_modified_time(fpath):
    
    statbuf = os.stat(fpath)
    f_mod_time = statbuf.st_mtime
    
    return f_mod_time


def is_file_older_than(fpath, **timedelta_args):
     
    mod_time = get_file_modified_time(fpath)
    
    now = dt.datetime.now()
    time_limit = now - dt.timedelta(**timedelta_args)
    
    print("mod_time: ", dt.datetime.utcfromtimestamp(mod_time))
    print("time_limit: ",time_limit)
    time_limit = time_limit.timestamp()

    return mod_time < time_limit