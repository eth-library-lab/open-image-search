#!/usr/bin/env python
# coding: utf-8

# used for basic data cleaning
# e.g. dropping NaN's & standardising column names
# it is not used for any feature engineering

import pandas as pd
import os, sys

sys.path.append('../search-model/src')
import utils
import argparse

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


def process_museum_plus_export(df):
    
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

    return df


def process_eth_metadata(df):
    
    # change url to lower resolution request (350x350px)
    df['image_url'] = df['image_url'].str.replace('resolution=superImageResolution','resolution=highImageResolution')
    
    return df


def add_id_column(df):
    
    df = df.reset_index(drop=True) 
    df.index = df.index.rename('id')
    df = df.reset_index()
    
    return df 

def main(input_metadata_path=None,
         output_dir=None) -> pd.DataFrame:


    if input_metadata_path.endswith(".xlsx"):
        df = pd.read_excel(input_metadata_path)
    else:
        df = pd.read_csv(input_metadata_path)

    print(f"loaded metadata file ({df.shape[0]} rows)")
    df = process_museum_plus_export(df)
    df = add_id_column(df)

    fname_output = os.path.basename(input_metadata_path)
    fname_output = fname_output.rsplit(".",maxsplit=1)[0] + ".csv"
    # save to interim folder for dataset
    fpath_output =  os.path.join(output_dir, fname_output)
    utils.prep_dir(fpath_output)
    # write out csv
    df.to_csv(fpath_output, index=False)
    print(f'wrote metadata file ({df.shape[0]} rows) to {fpath_output}')


    return df


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='metadata_cleaning')
    parser.add_argument('--input_metadata_fpath',  
                        type=str,
                        help="raw metadata csv to remove NaNs and duplicates from")
    parser.add_argument('--output_dir',  
                        type=str,
                        help="path to write cleaned csv to")
    args = parser.parse_args()

    print(args)


    main(input_metadata_path = args.input_metadata_fpath,
         output_dir = args.output_dir)


    # main(output_dir=settings.interim_metadata_dir,
    #      processed_img_dir=settings.processed_image_dir
    #      )
         