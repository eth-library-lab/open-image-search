import os
import pandas as pd
from tensorflow_recommenders.layers import factorized_top_k
from settings.settings import DEBUG, BASE_DIR
import numpy as np

# get the features vectors
feature_fpath = os.path.join(BASE_DIR ,"fixtures/features_prod.csv")
df_feat = pd.read_csv(feature_fpath, header=None)
# get the vectors from the df
img_features = df_feat.iloc[:,1:].values

def init_nn_model(img_features):
    # init the topk layer
    topk = factorized_top_k.BruteForce(k=100)
    #create the index
    topk = topk.index(img_features)

    return topk


def make_model_id_table(df_feat):

    model_index = df_feat.index.to_numpy()
    record_ids = df_feat[0].to_numpy()
    model_id_table =  np.vstack([model_index, record_ids]).T
    #sort according to record ids
    model_id_table = model_id_table[model_id_table[:, 1].argsort()]

    return record_ids, model_id_table


TOPK = init_nn_model(img_features)
RECORD_IDS, MODEL_ID_TABLE = make_model_id_table(df_feat)

# make sure df_feat is removed from memory
del df_feat


def knearest_ids(image_features, k=10):
    """
    use a Nearest Neighbours model to return the closest results
    and then map to record_ids
    """
    scores, model_indices = TOPK.call(image_features, k=k)
    model_indices = model_indices.numpy()[0]
    record_ids = RECORD_IDS[model_indices]

    return record_ids