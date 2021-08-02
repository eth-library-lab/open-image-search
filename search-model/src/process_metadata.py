#!/usr/bin/env python
# coding: utf-8


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
                 'timestamp': 'timestamp'}
    df = df.rename(columns=col_dict)
    df = df.drop(columns=['timestamp'])
    
    # change url to lower resolution request (350x350px) 
    df['image_url'] = df['image_url'].str.replace('resolution=superImageResolution','resolution=highImageResolution')
    
    return df


def main():

    for fsubpath in settings.metadata_csvs:

        fpath = os.path.join(settings.BASE_DIR, 'data','raw', fsubpath)
        df = pd.read_csv(fpath)
        print(f"loaded metadata file with {df.shape[0]} rows")

        df = process_eth_metadata(df)
        # save to folder for all institutions data
        output_dir = os.path.join(settings.BASE_DIR, 'data','interim','metadata')
        fpath =  os.path.join(output_dir, os.path.basename(fsubpath))
        utils.prep_dir(fpath)
        # write out csv
        df.to_csv(fpath, index=False)
        print(f'wrote metadata file to {fpath}')
    
    return


if __name__ == '__main__':
    
    main()