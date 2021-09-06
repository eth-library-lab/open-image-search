import os
import pandas as pd
import tensorflow as tf
from typing import Dict, Optional, Text, Tuple, Union
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
    topk = factorized_top_k.BruteForce(k=10)
    #create the index
    topk = topk.index(img_features)

    return topk

TOPK = init_nn_model(img_features)
RECORD_IDS = df_feat[0].to_numpy()
MODEL_ID_DICT = dict(zip(df_feat[0].tolist(), df_feat.index.tolist()))

# make sure df_feat is removed from memory
del df_feat

def model_to_record_ids(model_indices):
    """
    look up record ids from the given model indices
    """

    model_indices = model_indices.numpy()[0]
    record_ids = RECORD_IDS[model_indices]

    return record_ids


def record_to_model_ids(record_ids):
    """
    look up record ids from the given model indices
    """
    return [MODEL_ID_DICT[record_id] for record_id in record_ids]


def knearest_ids(image_features, k=10):
    """
    use a Nearest Neighbours model to return the closest results
    and then map to record_ids
    """
    scores, model_indices = TOPK.call(image_features, k=k)

    return model_indices

### TOPK with exclusions

def _take_along_axis(arr: tf.Tensor, indices: tf.Tensor) -> tf.Tensor:
    """Partial TF implementation of numpy.take_along_axis.
    See
    https://numpy.org/doc/stable/reference/generated/numpy.take_along_axis.html
    for details.
    Args:
    arr: 2D matrix of source values.
    indices: 2D matrix of indices.
    Returns:
    2D matrix of values selected from the input.
    """

    row_indices = tf.tile(
      tf.expand_dims(tf.range(tf.shape(indices)[0]), 1),
      [1, tf.shape(indices)[1]])
    gather_indices = tf.concat(
      [tf.reshape(row_indices, (-1, 1)),
       tf.reshape(indices, (-1, 1))], axis=1)

    return tf.reshape(tf.gather_nd(arr, gather_indices), tf.shape(indices))


# modified from tensorflow source code to prevent type error
def _exclude(scores: tf.Tensor, identifiers: tf.Tensor, exclude: tf.Tensor,
             k: int) -> Tuple[tf.Tensor, tf.Tensor]:
    """Removes a subset of candidates from top K candidates.
    For each row of inputs excludes those candidates whose identifiers match
    any of the identifiers present in the exclude matrix for that row.
    Args:
    scores: 2D matrix of candidate scores.
    identifiers: 2D matrix of candidate identifiers.
    exclude: 2D matrix of identifiers to exclude.
    k: Number of candidates to return.
    Returns:
    Tuple of (scores, indices) of candidates after exclusions.
    """

    idents = tf.expand_dims(identifiers, -1)
    exclude = tf.expand_dims(exclude, 1)

    isin = tf.math.reduce_any(tf.math.equal(idents, exclude), -1)

    # Set the scores of the excluded candidates to a very low value.
#     adjusted_scores = (scores - tf.cast(isin, tf.float32) * 1.0e5)
    
    ##### cast input scores to prevent type error
    adjusted_scores = (tf.cast(scores, tf.float64) - tf.cast(isin, tf.float64) * 1.0e5)

    k = tf.math.minimum(k, tf.shape(scores)[1])

    _, indices = tf.math.top_k(adjusted_scores, k=k)

    return _take_along_axis(scores,
                          indices), _take_along_axis(identifiers, indices)


def top_k_with_exclusions(query, ids_to_exclude=set(), k=10):
    """
    topk: instance of tensorflow TopK class
    query: vector to find similar records
    exclusions: ids of the records to exclude
    k: number of results to return
    """

    exclusions = tf.constant([list(ids_to_exclude)])
    adjusted_k = k + exclusions.shape[1]
    print("adjusted_k: ", adjusted_k)
    x, y = TOPK.call(queries=query, k=adjusted_k)
    scores, indices = _exclude(x, y, exclude=exclusions, k=k)

    return indices