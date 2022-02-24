# get create a feature vector based on the classification of each record


import pandas as pd
from collections import defaultdict
import numpy as np

def create_class_dict(ser):
    
    # use a default dict to return -1 in case key is not found
    class_dict = defaultdict(lambda: -1)
    classes = np.unique(ser)
    indices = np.arange(1, len(classes)+1)
    class_dict.update(dict(zip(classes, indices)))
    
    return class_dict


def tokenize_series(ser):
    """use regex to tokenize a series of strings.
    regex pattern from scikit-learn 
    """
    tokenizer = re.compile(r"(?u)\b\w\w+\b")    
    ser = ser.fillna("").str.lower()
    ser = ser.apply(tokenizer.findall)
    return ser

def tokens_to_ragged_feature_vector(ser:pd.Series, class_dict:defaultdict) -> pd.Series:

    ser = ser.apply(lambda lst: [class_dict[el] for el in lst])

    return ser

def process_series(input_ser, vocab_ser):
    # tokenize strings in pandas series
    
    ser = tokenize_series(input_ser)

    # load vocabulary

    class_dict = create_class_dict(vocab_ser)

    # create feature vector using vocab hash table
    ser = tokens_to_ragged_feature_vector(ser,class_dict)
    return ser
# output vector

    # df = pd.read_csv("../../data/processed/lists/MaterialTechnique.csv")
    # vocab_ser = df['name']