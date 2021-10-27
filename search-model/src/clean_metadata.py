#!/usr/bin/env python
# coding: utf-8

# used for basic data cleaning
# e.g. dropping NaN's & standardising column names
# it is not used for any feature engineering

import pandas as pd
import os, sys

sys.path.append('..')
import settings
import utils

def clean_df(df):
    """drop duplicates and empty rows"""
    orig_shape=df.shape
    df = df.dropna(how='all')
    #keep rows that are not duplicated 
    fltr = ~df.duplicated()
    df = df.loc[fltr,:]
    
    dropped_rows = orig_shape[0] - df.shape[0]
    print(f"dropped {dropped_rows} NaN or duplicated rows")
    
    return df    


def process_eth_metadata(df):
    
    df = clean_df(df)
    col_dict = { 'recordID': 'record_id',
                 'imageURL': 'image_url',
                 'invNr': 'inventory_number',
                 'person': 'person',
                 'date': 'date',
                 'title': 'title',
                 'classification': 'classification',
                 'matTec': 'material_technique',
                 'institutionIsil': 'institution_isil',
                 'recordURL': 'record_url',
                 'imageLicence': 'image_licence',
                 'relations':'relations',
                 'timestamp': 'timestamp'}
    df = df.rename(columns=col_dict)

    if 'timestamp' in df.columns:
        df = df.drop(columns=['timestamp'])
    
    # change url to lower resolution request (350x350px)
    df['image_url'] = df['image_url'].str.replace('resolution=superImageResolution','resolution=highImageResolution')
    
    return df

def add_id_column(df):
    
    df = df.reset_index(drop=True) 
    df.index = df.index.rename('id')
    df = df.reset_index()
    
    return df 

def main(output_dir=settings.interim_metadata_dir,  
         processed_img_dir=settings.processed_image_dir):


    # if there is one or more metadata csvs process them, else create a csv with just the filenames
    if settings.metadata_csvs:
        for fpath_input in settings.metadata_csvs:
            if fpath_input.endswith(".xlsx"):
                df = pd.read_excel(fpath_input)
            else:
                df = pd.read_csv(fpath_input)

            print(f"loaded metadata file ({df.shape[0]} rows)")
            df = process_eth_metadata(df)
            df = add_id_column(df)

            fname_output = os.path.basename(fpath_input)
            fname_output = fname_output.rsplit(".",maxsplit=1)[0] + ".csv"
            # save to interim folder for dataset
            fpath_output =  os.path.join(output_dir, fname_output)
            utils.prep_dir(fpath_output)
            # write out csv
            df.to_csv(fpath_output, index=False)
            print(f'wrote metadata file ({df.shape[0]} rows) to {fpath_output}')

    else:
        #list images in the input directory and put them in a dataframe
        img_list = utils.get_list_of_files_in_dir(processed_img_dir, file_types = ['jpg', 'jpeg','png'], keep_fldr_path=True)
        df = pd.DataFrame({"image_url":img_list})
        df["id"] = df.index.to_list()
        df = add_id_column(df)

        # save to interim folder for dataset
        fpath_output =  os.path.join(output_dir, os.path.basename(settings.processed_image_dir) + ".csv")
        utils.prep_dir(fpath_output)
        # write out csv
        df.to_csv(fpath_output, index=False)
        print(f'wrote metadata file to {fpath_output}')

    return df


if __name__ == '__main__':
    
    main(output_dir=settings.interim_metadata_dir,
         processed_img_dir=settings.processed_image_dir
         )
         