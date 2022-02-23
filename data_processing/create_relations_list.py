# creates a list/vocabulary of classification terms
# To be used later to tag text that contains these terms

import pandas as pd
import numpy as np
import re
import os, sys
import argparse
from collections import defaultdict

sys.path.append('..')
import export_metadata


def load_df(data_dir):
    # list of files to load classification terms from
    fpaths = [
        (data_dir, "raw","ethz","metadata","imageSearch_relations.xlsx"),
    ]

    df_list = []
    for fpath in fpaths:
        fpath = os.path.join(*fpath)
        if fpath.endswith(".xlsx"):
            df = pd.read_excel(fpath)
        else:
            df = pd.read_csv(fpath)
        
        df_list.append(df)

    df = pd.concat(df_list)
    print(f"loaded metadata file with {df.shape[0]} rows")

    return df


def flatten_series_of_lists(ser:pd.Series):
    """
    flatten a series of lists where the relationship between the index and the values 
    needs to be maintained
    ser: pd.Series where the values are lists
    """
    
    indices = []
    keys = []
    for index, row in ser.iteritems():
        if type(row) != list:
            pass

        else:
            for key in row:
                indices.append(index)
                keys.append(key)

    return pd.Series(index=indices, data=keys, name=ser.name)


def split_and_flatten_series(ser, split_char=None):
    
    ser = ser.str.lower()
    # split into series of lists strings based split_char
    if split_char:
        ser = ser.str.split(split_char)
        # flatten series of lists
        ser = flatten_series_of_lists(ser)

    # strip whitespace from strings
    if ser.dtype == "O":
        ser = ser.str.strip()
    
    return ser


def has_numbers(inputString):
    "return true if there are numbers in the input string. uses regex"
    return bool(re.search(r'.+\d.+', inputString))


def make_relationships_ser(ser_relations):
    """
    make a flat, unique series of relationship types from an input series of semi-colon separated relationship, inventory_number tuples
    
    e.g. "Entwurf zu, D 018051; nach, D 018052"
    """
    
    tser = split_and_flatten_series(ser_relations, split_char=";")
    # relation
    tdf = tser.str.split(",", n=1, expand=True)
    tdf = tdf.rename(columns={0:"relationship_type",1:"inventory_number"})
    # filter out entries that only have the inventory_number present (no relationship_type specified) to the second column
    ser = tdf["relationship_type"].dropna().astype(str)
    fltr = ser.apply(has_numbers)
    ser = ser.loc[~fltr]
    ser = ser.str.replace("doublette","dublette")
    ser = ser.str.lower()
    ser = ser.drop_duplicates().reset_index(drop=True)

    return ser


def main():

    data_dir = "../data"
    df = load_df(data_dir)
    
    col_name="relations"
    #### relationship types ####
    if col_name in df.columns:
        ser = df[col_name]
        ser = make_relationships_ser(ser)
        
        # write classification csv and fixture
        model_name = 'Relationship'
        ser.name = "name"
        tdf = pd.DataFrame(ser)
        print(f"created list of {tdf.shape[0]} terms for model: {model_name}")
        # output csv
        output_dir = os.path.join(data_dir, "processed","lists")
        csv_path = os.path.join(output_dir, model_name+".csv")
        tdf.to_csv(csv_path, index=False)

        # write json fixture
        fixture_lst = export_metadata.df_to_fixture_list(tdf,
                    app_name='ImageSearch',
                    model_name=model_name,
                    use_df_index_as_pk=True,
                    create_datetimefield_name="created_date",
                    created_by_field_name=None,
                    )
        export_metadata.write_fixture_list_to_json(fixture_lst,
                                model_name,
                                output_dir,
                                file_name_modifier="")


if __name__ ==  '__main__':

    main()