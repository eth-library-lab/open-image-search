#!/usr/bin/env python
# coding: utf-8

## Export metadata to django fixture

import os, sys
import pandas as pd
import json
from datetime import datetime as dt

sys.path.append('../src')
import utils
import settings


def create_django_datetimestamp(dt_object=None):
    
    if dt_object==None:
        created_time = dt.now()
    else:
        created_time = dt_object
    # for django, timefield must be in format YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
    # e.g. "2020-05-26T11:40:56+01:00"
    created_time = created_time.strftime('%Y-%m-%dT%H:%M:%S+01:00')
    
    return created_time


def df_to_json_fixture(df,
                       app_name,
                       model_name,
                       file_name_modifier='',
                       output_folder=None,
                       use_df_index_as_pk=False,
                       pk_start_num=1000,
                       create_datetimefield_name=None,
                       created_by_field_name=None,
                       created_by_value=1):
    
    """
    convert a dataframe to a django fixture file to populate an database
    each column becomes a field in the record
    
    df,
    app_name: app name in django,
    model_name: model name in django
    folder: destination folder to output files to
    use_df_index_as_pk: if True df.index will become the primary key for records
    no checks are performed
    pk_start_num: if use_df_index_as_pk is False, primary keys will start at this
    number
    create_datetimefield_name: set to the name of the datetimefield for
    recording when a record is created.
    """

    model = "{}.{}".format(app_name, model_name)
    
    if create_datetimefield_name:
        created_time = create_django_datetimestamp()
        df[create_datetimefield_name] = created_time
    
    if created_by_field_name:
        df[created_by_field_name] = created_by_value
    
    fixture_lst = []
    for i, row in df.reset_index().iterrows():
        
        if use_df_index_as_pk==True:       
            pk = row['index']
        
        else:
            pk = i+pk_start_num
        
        fields_dict = row.drop(['index']).to_dict()
        
        record = {'model':model, 
               'pk':pk,
               'fields': fields_dict}
        fixture_lst.append(record)
    
    fname = model_name+'{}.json'.format(file_name_modifier)
    if output_folder==None:
        output_folder = '../data/processed/fixtures'
        
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    fpath = os.path.join(output_folder, fname)
    
    if os.path.exists(fpath):
        raise Exception('did not save, file already exists: {}'.format(fpath))

    with open(fpath, 'w') as f:
        json.dump(fixture_lst, 
                  f, 
                  skipkeys=False, 
                  sort_keys=False)

    return fixture_lst


def get_list_of_metadata_csvs(metadata_dir):

    fpaths = []

    for fname in os.listdir(metadata_dir):
        if fname.endswith('.csv'):
            fpath = os.path.join(metadata_dir, fname)
            fpaths.append(fpath)

        return fpaths

def load_csvs_into_df(fpaths):
    """
    fpaths: list of csv filepaths to concatenate into a single pd.DataFrame
    """
    df_list = []
    for fpath in fpaths:

        df = pd.read_csv(fpath, index_col='record_id')
        df_list.append(df)

    df = pd.concat(df_list)    
    df = df.sort_values(by='record_id')
    df = df.reset_index()

    return df


def main():

    metadata_dir = os.path.join(settings.BASE_DIR, 'data','interim','metadata')

    fpaths = get_list_of_metadata_csvs(metadata_dir)
    df = load_csvs_into_df(fpaths)
 

    fixture_dict = df_to_json_fixture(df,
                    'ImageSearch',
                    'ImageMetadata',
                    file_name_modifier='',
                    output_folder=None,
                    use_df_index_as_pk=False,
                    pk_start_num=1000,
                    create_datetimefield_name='created_date',
                    created_by_field_name=None,
                    created_by_value=1)

    return fixture_dict


if __name__ == '__main__':

    fixture_dict = main()


