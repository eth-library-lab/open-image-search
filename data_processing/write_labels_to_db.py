"""
script to write vocabulary labels to the database
e.g. MaterialTechnique, Classification  
"""

import argparse

from sqlalchemy import Table, MetaData
from utils_db import create_db_engine, series_to_values_dicts, write_values_dict_to_db
import pandas as pd
from typing import List


def load_series(fpath:str)->pd.Series:
    """
    load a csv of labels as a series
    """
    df = pd.read_csv(fpath)
    ser = df['name']
    return ser


def write_labels_from_series(ser:pd.Series, table_name:str):
    """
    write the given series of labels to the database
    ser: labels to write to DB
    table_name: table in DB to write to 
    """
    # load values_dict of terms

    # prep values and insert into database
    engine = create_db_engine()
    values_dict = series_to_values_dicts(ser,"name")
    
    result_list = write_values_dict_to_db(engine, 
                                  values_dict,
                                  table_name=table_name)

    print(f"wrote {len(result_list)} records to db table '{table_name}'")


def main():

    # Classification
    fpath = "../data/processed/lists/Classification.csv"
    ser = load_series(fpath)
    table_name="ImageSearch_classification"
    write_labels_from_series(ser, table_name)

    # MaterialTechnique
    fpath = "../data/processed/lists/MaterialTechnique.csv"
    ser = load_series(fpath)
    table_name="ImageSearch_materialtechnique"
    write_labels_from_series(ser, table_name)

    # Relationship
    fpath = "../data/processed/lists/Relationship.csv"
    ser = load_series(fpath)
    table_name="ImageSearch_relationship"
    write_labels_from_series(ser, table_name)


if __name__ == "__main__":

    main()
