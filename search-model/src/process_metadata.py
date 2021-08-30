#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import re
import os, sys
import argparse

sys.path.append('..')
import settings
import utils

def get_record_ids_from_features_df(df_feat):
    """
    using the df from the calculated features csv
    add a column with record ids
    return df
    """
    
    df_fpath = df_feat.iloc[:,[0]]
    print("df_fpath: \n\n",df_fpath,"\n\n")
    df_fpath = df_fpath.rename(columns={0:"fpath"})
    df_fpath['record_id'] = df_fpath["fpath"].str.rsplit(pat="/", n=1, expand=True)[1]
    df_fpath['record_id'] = df_fpath['record_id'].str.split(pat=".", n=1, expand=True)[0]
    df_fpath.index.rename("model_id", inplace=True)
    
    return df_fpath

def use_fpaths_to_insert_model_ids_into_df_meta(df_fpath, df_meta):
    """join metadata to fpaths and model ids"""
    
    df_meta.index.rename("db_id", inplace=True)
    df_meta = df_meta.reset_index()
    df_meta["record_id"] = df_meta["record_id"].astype("Int64")
    df_fpath["record_id"] = df_fpath["record_id"].astype(int)
    df = df_fpath.merge(df_meta, how="left", on="record_id" )
    df.index.rename("model_id", inplace=True)
    
    return df


def series_of_lists_to_array(ser, fill_value_index=None):
    """
    transform a series of lists (like returned by str.split()) into an array.
    By default, lists with differing lengths will be padded with None or
    fill_value_index can be used to select an element from each list to pad with.
    e.g. fill_value_index=-1 will pad the array to the right with the last element from each list 
    modified from https://stackoverflow.com/questions/10346336/list-of-lists-into-numpy-array
    
    """
    x=ser.values
    length=(np.vectorize(len)(x)).max()
    if fill_value_index==None:
        y=np.array([xi+[None]*(length-len(xi)) for xi in x])
    
    if type(fill_value_index)==int:
        y=np.array([xi+[xi[fill_value_index]]*(length-len(xi)) for xi in x])

    return y


def series_of_string_years_to_min_max_years(ser):
    """
    get min and max years from date column
    assumes the earliest and latest years (in digits) in the string
    are the earlist and latest years
    ser:pd.Series, date column from the metadata dataframe
    returns two pandas series: min_years, max_years
    """
#     ser_index = ser.index
    fltr = ser.isna()
    ser = ser.loc[~fltr]
    print("number of rows that were missing values: {:,}".format(fltr.sum()))
    # assumes that all years are after 99 A.D.
    ptrn = re.compile(r"[0-9]{3,4}")
    years = ser.apply(ptrn.findall)
    years = series_of_lists_to_array(years, fill_value_index=-1)
    years = years.astype(int)
    min_years = np.min(years, axis=1)
    max_years = np.max(years, axis=1)
    
    return min_years, max_years, ser.index


def insert_min_max_years_into_df(df_meta, min_years, max_years, index):
    
    df_meta.loc[index,"min_year"] = min_years
    df_meta.loc[index,"max_year"] = max_years
    # convert from floats to pandas ints
    df_meta.loc[:,["min_year","max_year"]] = df_meta.loc[:,["min_year","max_year"]].astype("Int64")
    #fill in NaN's with -1 to still use numpy int comparisons
    fltr = df_meta[["min_year","max_year"]].isna().any(axis=1)
    df_meta.loc[fltr,["min_year","max_year"]] = -1
    
    return df_meta


def insert_years_from_text(df):

    ser = df["date"].dropna()
    min_years, max_years, index = series_of_string_years_to_min_max_years(ser)
    df = insert_min_max_years_into_df(df, min_years, max_years, index)

    return df


def process_eth_metadata(df):
    
    
    return df



def main(args=None):


    input_dir = settings.interim_metadata_dir
    if args:
        input_dir = args.metadata_dir

    # if there is one or more metadata csvs process them, else create a csv with just the filenames
    flist = utils.get_list_of_files_in_dir(input_dir,file_types=['csv'])

    if flist:
        # load metadata interim file
        df_list = [pd.read_csv(fpath) for fpath in flist]
        df_meta = pd.concat(df_list)
        print(f"loaded metadata file with {df_meta.shape[0]} rows")

        # join with id numbers from the calculated features
        df_feat = pd.read_csv(settings.features_fpath, usecols=[0,], header=None)
        df_fpath = get_record_ids_from_features_df(df_feat)
        print("df_fpath: \n\n", df_fpath)
        df = use_fpaths_to_insert_model_ids_into_df_meta(df_fpath, df_meta)

        ## create new feature columns
        # min/max years
        df = insert_years_from_text(df)

        print(df.head())
        # df = process_eth_metadata(df)
        # # save to interim folder for dataset
        # fpath_output =  os.path.join(output_dir, os.path.basename(fpath_input))
        # utils.prep_dir(fpath_output)
        # # write out csv
        # df.to_csv(fpath_output, index=False)
        # print(f'wrote metadata file to {fpath_output}')

    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='settings file')
    parser.add_argument('--metadata_dir',
                        type=str,
                        default=None,
                        help='print out main settings')
    args = parser.parse_args()

    main(args=args)