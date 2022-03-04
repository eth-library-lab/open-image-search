"""utils for labelling text based features"""
import numpy as np
import pandas as pd
from sqlalchemy import text, MetaData, Table, select
import json
import re
from collections import defaultdict

from utils_db import create_db_engine


def create_class_dict(ser):
    
    # use a default dict to return -1 in case key is not found
    class_dict = defaultdict(lambda: -1)
    classes = np.unique(ser)
    indices = np.arange(1, len(classes)+1)
    class_dict.update(dict(zip(classes, indices)))
    
    return class_dict


def load_feature_types(table_name:str)-> defaultdict:
    """
    query db to get list of types e.g. classification types
    """

    feature_tables =["ImageSearch_classification", 
                     "ImageSearch_materialtechnique",
                     "ImageSearch_relationship",
                    ]
    assert table_name in feature_tables, f"requested table {table_name} must be one of {feature_tables}"

    engine = create_db_engine()

    # reflect the existing table properties
    metadata_obj = MetaData()
    t = Table(table_name, metadata_obj, autoload_with=engine)

    # query the db
    s = select(t.c.id, t.c.name)
    conn = engine.connect()
    res = conn.execute(s)

    res_d = defaultdict(lambda: -1)
    for row in res:
        res_d[row.name] = row.id    

    return res_d


def load_fixture_to_dict(fpath:str, synonyms=None) -> defaultdict:
    
    with open(fpath,'r') as f:
        objects = json.load(f)
    
    d = defaultdict(lambda: -1)
    for obj in objects:
        val = obj["pk"]
        key = obj["fields"]["name"]
        d[key] = val


    # temporary, replace with proper table of synomyms and translations
    if synonyms:
        for orig,alt in synonyms.items():
            d[alt] = d[orig]

    return d


def tokenize_series(ser):
    """use regex to tokenize a series of strings.
    regex pattern from scikit-learn 
    """
    tokenizer = re.compile(r"(?u)\b\w\w+\b")
    ser = ser.apply(tokenizer.findall)
    return ser


def split_series(ser,sep=",")->pd.Series:

    ser = ser.str.split(sep, expand=False)
    
    return ser


def tokens_to_ragged_feature_vector(ser:pd.Series, class_dict:defaultdict) -> pd.Series:

    cls_keys = class_dict.keys()
    ser = ser.apply(lambda lst: [class_dict[el] for el in lst if el in cls_keys])

    return ser


def process_series(input_ser, class_dict):

    ser = input_ser.fillna("").str.lower()
    # tokenize strings in pandas series
    # ser = tokenize_series(ser)
    ser = split_series(ser)
    # create feature vector using vocab hash table
    ser = tokens_to_ragged_feature_vector(ser, class_dict)

    return ser