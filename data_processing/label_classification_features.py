# get create a feature vector based on the classification of each record


import pandas as pd
from collections import defaultdict
import numpy as np
import json
import re
from sqlalchemy import text

from utils_db import create_db_engine

def create_class_dict(ser):
    
    # use a default dict to return -1 in case key is not found
    class_dict = defaultdict(lambda: -1)
    classes = np.unique(ser)
    indices = np.arange(1, len(classes)+1)
    class_dict.update(dict(zip(classes, indices)))
    
    return class_dict


def load_classification_types()-> defaultdict:
    """
    query db to get list of classification types
    """

    engine = create_db_engine()
    STMT = """
    SELECT id, name
    FROM "ImageSearch_Classification";
    """
    stmt = text(STMT)
    
    with engine.connect() as conn:
        result = conn.execute(stmt)

    res_d = defaultdict(lambda: -1)
    for row in result:
        print("found existing: ", row.id,"  ", row.name)
        res_d[row.name] = row.id    

    return res_d


def load_fixture_to_dict(fpath:str) -> defaultdict:
    
    with open(fpath,'r') as f:
        objects = json.load(f)
    
    d = defaultdict(lambda: -1)
    for obj in objects:
        val = obj["pk"]
        key = obj["fields"]["name"]
        d[key] = val


    # temporary, replace with proper table of synomyms and translations
    synonyms = {"druckgraphik":"druckgrafik",}
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
    print(ser)
    # create feature vector using vocab hash table
    ser = tokens_to_ragged_feature_vector(ser, class_dict)

    return ser




if __name__ == '__main__':

    class_dict = load_fixture_to_dict("../data/processed/lists/Classification.json")

    df = pd.read_csv("../data/interim/zbz/metadata/metadata.csv", usecols=["classification",])
    input_ser = df['classification']

    output_ser = process_series(input_ser, class_dict)
    
    print(output_ser.head())

    # df = pd.read_csv("../../data/processed/lists/MaterialTechnique.csv")
    # vocab_ser = df['name']