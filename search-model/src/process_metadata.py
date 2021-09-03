#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import re
import os, sys
import argparse
from collections import defaultdict

sys.path.append('..')
import settings
import utils
import export_metadata


def get_record_ids_from_fpaths(ser_fpaths):
    """
    using the df from the calculated features csv
    add a column with record ids
    return df
    """

    ser = ser_fpaths.str.rsplit(pat="/", n=1, expand=True)[1]
    ser = ser.str.split(pat=".", n=1, expand=True)[0]
    ser.name = 'record_id'
    ser.index.rename("model_id", inplace=True)
    
    return ser


def create_class_dict(ser):
    
    # use a default dict to return -1 in case key is not found
    
    class_dict = defaultdict(lambda: -1)
    classes = np.unique(ser)
    indices = np.arange(len(classes))
    class_dict.update(dict(zip(classes, indices)))
    
    return classes, indices, class_dict


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


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


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
    
    df_meta.loc[index,"year_min"] = min_years
    df_meta.loc[index,"year_max"] = max_years
    # convert from floats to pandas ints
    df_meta.loc[:,["year_min","year_max"]] = df_meta.loc[:,["year_min","year_max"]].astype("Int64")
    #fill in NaN's with -1 to still use numpy int comparisons
    fltr = df_meta[["year_min","year_max"]].isna().any(axis=1)
    df_meta.loc[fltr,["year_min","year_max"]] = -1
    
    return df_meta


def insert_years_from_text(df):

    ser = df["date"].dropna()
    min_years, max_years, index = series_of_string_years_to_min_max_years(ser)
    df = insert_min_max_years_into_df(df, min_years, max_years, index)

    return df


def make_flat_relationships_table(df_meta):
    """
    flatten semi-colon separated lists of  relationships between works
    """
    
    tser = split_and_flatten_series(df_meta["relations"], split_char=";")
    tdf = tser.str.split(",", n=1, expand=True)
    tdf = tdf.rename(columns={0:"relationship_type",1:"inventory_number"})
    fltr = tdf["relationship_type"].notna() & tdf["inventory_number"].isna() & tdf["relationship_type"].apply(has_numbers)
    tdf.loc[fltr,"inventory_number"] = tdf.loc[fltr, "relationship_type"]
    tdf.loc[fltr,"relationship_type"] = "undefined"
    tdf["relationship_type"] = tdf["relationship_type"].str.replace("doublette","dublette")
    tdf["inventory_number"]= tdf["inventory_number"].str.strip()

    return tdf


def make_df_of_relationship_types(ser):
    """
    ser: pd.Series, column of all relationship types (non unique)
    return dataframe with unique values
    """

    # filter out na and undefined
    fltr = ser != "undefined"
    ser = ser.loc[fltr]
    
    classes, indices, class_dict = create_class_dict(ser)
    df_relationship = pd.DataFrame(data={"name":classes}, index=indices)

    return df_relationship


def nest_relationship_type_ids(df_rel_types, df_relationships):
    """
    convert the flat table of relationship types as text, into lists of ids   

    df_rel_types: pd.DataFrame, the table of unique relationship types. used to create the id dictionary
    df_relationships: pd.DataFrame, the flat table of relationship types as text
    """
    # map ids into the flat list of relationship types
    rel_types_dict = dict(zip(df_rel_types['name'].to_list(), df_rel_types.index.to_list()))
    df_relationships['relationship_type_id'] = df_relationships['relationship_type'].map(rel_types_dict)
    # create a series with lists of relationship ids (for Django manytomany field)
    df_rel_types_list = df_relationships[['relationship_type_id']].sort_index()
    df_rel_types_list = df_rel_types_list.reset_index().rename(columns={"index":"record_id"})
    df_rel_types_list = df_rel_types_list.drop_duplicates()
    df_rel_types_list = df_rel_types_list.groupby('record_id').agg({"relationship_type_id":lambda x: x.tolist()})

    return df_rel_types_list


def nest_class_ids(class_dict, ser_to_encode):
    """
    convert the flat table of relationship types as text, into lists of ids   

    df_rel_types: pd.DataFrame, the table of unique relationship types. used to create the id dictionary
    df_relationships: pd.DataFrame, the flat table of relationship types as text

    returns: pd.DataFrame
    """
    ser_name = ser_to_encode.name
    # map ids into the flat list of relationship types
    ser = ser_to_encode.map(class_dict)
    # create a series with lists of relationship ids (for Django manytomany field)
    tdf = ser.sort_index().reset_index().rename(columns={"index":"record_id"})
    tdf = tdf.drop_duplicates()
    # nest encoded ids 
    tdf = tdf.groupby('record_id').agg({ser_name:lambda x: x.tolist()})

    return tdf


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
    df_feat = pd.read_csv(settings.features_fpath, header=None)
    # replace fpaths with record_ids 
    # ? replace with db ids later?
    df_feat.iloc[:,0] = get_record_ids_from_fpaths(df_feat.iloc[:,0])
    df_feat.to_csv(settings.features_fpath.replace('.csv','_prod.csv'),index=False,header=False)
    ## create new feature columns
    # min/max years
    df_meta = insert_years_from_text(df_meta)

    #### relationship types ####
    
    # extract information
    df_relationships = make_flat_relationships_table(df_meta)
    ser = df_relationships['relationship_type']
    fltr = ser != "undefined"
    ser = ser.loc[fltr]

    classes, indices, class_dict = create_class_dict(ser)
    df_rel_types = pd.DataFrame(data={"name":classes}, index=indices)
    df_rel_types = make_df_of_relationship_types(ser)

    # write relationship types fixture
    model_name = 'Relationship'
    fixture_lst = export_metadata.df_to_fixture_list(df_rel_types,
                app_name='ImageSearch',
                model_name=model_name,
                use_df_index_as_pk=True,
                create_datetimefield_name="created_date",
                created_by_field_name=None,
                )
    export_metadata.write_fixture_list_to_json(fixture_lst,
                            model_name,
                            settings.fixtures_dir,
                            file_name_modifier="")

    # encode relationship types in main metadata df
    df_relationships = df_relationships.loc[df_relationships['relationship_type'] != 'undefined',:]
    
    # df_rel_types_list = nest_relationship_type_ids(df_rel_types, df_relationships)
    ser.name = "relationship_type_id"
    df_rel_types_list = nest_class_ids(class_dict, ser)
    df_meta = df_meta.merge(df_rel_types_list, how='left',left_index=True, right_index=True)


    #### classification types ####

    col_name = 'classification'
    
    ser = df_meta[col_name]
    ser = ser.str.strip().replace("",np.nan).dropna() 
    
    classes, indices, class_dict = create_class_dict(ser)

    # write classification fixture
    tdf = pd.DataFrame(data={"name":classes}, index=indices)
    model_name = 'Classification'
    fixture_lst = export_metadata.df_to_fixture_list(tdf,
                app_name='ImageSearch',
                model_name=model_name,
                use_df_index_as_pk=True,
                create_datetimefield_name="created_date",
                created_by_field_name=None,
                )
    export_metadata.write_fixture_list_to_json(fixture_lst,
                            model_name,
                            settings.fixtures_dir,
                            file_name_modifier="")

    # encode classifications in df
    df_meta[col_name + '_id'] = df_meta[col_name].map(class_dict)


    #### material_technique ####

    col_name = 'material_technique'
    ser = df_meta[col_name].dropna()
    ser = split_and_flatten_series(ser, split_char=",")
    classes, indices, class_dict = create_class_dict(ser)

    # write fixture
    tdf = pd.DataFrame(data={"name":classes}, index=indices)
    model_name = 'MaterialTechnique'
    fixture_lst = export_metadata.df_to_fixture_list(tdf,
                app_name='ImageSearch',
                model_name=model_name,
                use_df_index_as_pk=True,
                create_datetimefield_name="created_date",
                created_by_field_name=None,
                )
    export_metadata.write_fixture_list_to_json(fixture_lst,
                            model_name,
                            settings.fixtures_dir,
                            file_name_modifier="")

    # encode material_technique in df
    ser.name = col_name + "_id"
    tdf = nest_class_ids(class_dict, ser)
    df_meta = df_meta.merge(tdf, how='left', left_index=True, right_index=True)


    #### Person types ####
    # extract info
    # create fixture
    # encode in df


    #### institution ####

    col_name = 'institution_isil'
    ser = df_meta[col_name].dropna()
    classes, indices, class_dict = create_class_dict(ser)

    # write fixture
    tdf = pd.DataFrame(data={"name":classes}, index=indices)
    model_name = 'Institution'
    fixture_lst = export_metadata.df_to_fixture_list(tdf,
                app_name='ImageSearch',
                model_name=model_name,
                use_df_index_as_pk=True,
                create_datetimefield_name="created_date",
                created_by_field_name=None,
                )
    export_metadata.write_fixture_list_to_json(fixture_lst,
                            model_name,
                            settings.fixtures_dir,
                            file_name_modifier="")

    # encode material_technique in df
    
    df_meta[col_name + "_id"] = df_meta[col_name].map(class_dict)

    # df = process_eth_metadata(df)

    #### FINISH ####
    # after all process/feature engineering is finished
    # write out finshed metadata as json fixture and csv
    df_meta.index.name ='index'
    df_meta = df_meta.drop(columns=["relations"])
    fk_cols = ['relationship_type_id', 'classification_id', 'material_technique_id', 'institution_isil_id'] 
    df_meta[fk_cols] = df_meta[fk_cols].replace(-1,np.nan) 
    model_name='ImageMetadata'
    fixture_lst = export_metadata.df_to_fixture_list(df_meta,
                    app_name='ImageSearch',
                    model_name=model_name,
                    use_df_index_as_pk=False,
                    pk_start_num=1000,
                    create_datetimefield_name="created_date",
                    created_by_field_name=None,
                    created_by_value=1)
    export_metadata.write_fixture_list_to_json(fixture_lst,
                            model_name,
                            settings.fixtures_dir,
                            file_name_modifier="")

    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='settings file')
    parser.add_argument('--metadata_dir',
                        type=str,
                        default=settings.interim_metadata_dir,
                        help='print out main settings')
    args = parser.parse_args()

    main(args=args)