"""
script to add directory of images to database 
and copy/rename files with db assigned ids 
"""

import argparse

from sqlalchemy import Table, MetaData
from utils_db import create_db_engine, series_to_values_dicts, write_values_dict_to_db
import pandas as pd
from typing import List

def from_series(ser:pd.Series):
    
    # load values_dict of terms

    # prep values and insert into database
    engine = create_db_engine()
    values_dict = series_to_values_dicts(ser,"name")
    table_name="ImageSearch_materialtechnique"
    res = write_values_dict_to_db(engine, 
                                  values_dict,
                                  table_name=table_name)
    res_ids = [r[0] for r in res]
    print(f"wrote {len(res_ids)} records to db table '{table_name}'")


if __name__ == "__main__":

    description= """creates a database records for classification types"""
    parser = argparse.ArgumentParser(description=description)
    args = parser.parse_args()
    fpath = "../data/processed/lists/MaterialTechnique.csv"
    df = pd.read_csv(fpath)
    ser = df['name']
    from_series(ser)