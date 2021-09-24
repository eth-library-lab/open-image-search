# Load a pretrained model and save as a recommender

import pandas as pd
import os, sys

import tensorflow as tf
import tensorflow_datasets as tfds
import tensorflow_recommenders as tfrs
from tensorflow.keras.applications.xception import preprocess_input
from tensorflow.keras.preprocessing import image
from typing import Union, Optional, Tuple, Dict, Text

from PIL import Image
import matplotlib.pyplot as plt 
from time import time
import numpy as np

sys.path.append('../src')

import settings
import utils
from preprocess_images import resize_image
from utils_tf import ImageNormalizer, parse_image_func

def create_retrieval_model(query_model, features, indentifiers, verbose=1):
    """
    query_model: tensorflow model used to calculate features from the input
    features: np.array, feature vectors to create index for
    indentifier_ids: np.array, integer id for each feature
    """

    # newInput = Input(batch_shape=(1,128,128,3))
    # newOutputs = oldModel(newInput)
    # newModel = Model(newInput,newOutputs)
    
    # Create a model that takes in raw query features and returns ids
    retrieval_model = tfrs.layers.factorized_top_k.BruteForce(query_model=query_model)
    # retrieval_model = tfrs.layers.factorized_top_k.ScaNN(query_model=ftx_model)  

    # create the retrieval index
    candidates = tf.constant(features, dtype=tf.float32)
    identifiers = tf.constant(indentifiers, dtype=tf.int32)
    
    if verbose:
        t0=time()
        print("creating feature index")
        
    retrieval_model.index(candidates, identifiers)

    if verbose:
        t_delta= time() - t0
        print("created feature index in {:.3}s".format(t_delta))
        
    retrieval_model.compile()
    
    return retrieval_model


class RetrievalExclusionModel(tf.keras.Model):
    
    def __init__(self, retrieval_model):
        super(RetrievalExclusionModel, self).__init__(name='retrieval_exclusion')
        self.model = retrieval_model

    def call(self,
             queries: Union[tf.Tensor, Dict[Text, tf.Tensor]],
             exclusions: tf.Tensor,
             k: Optional[int] = 25
            ) -> Tuple[tf.Tensor, tf.Tensor]:

        return self.model.query_with_exclusions(
            queries,
            exclusions,
            k=k)


# testing the model

def plot_image_from_fpath(fpath):

    img = Image.open(fpath)
    plt.imshow(img)
    plt.show()
    
    return

def print_list_of_ids(list_of_ids, image_fldr, max_to_print=10):
    
    for _id in list_of_ids[:max_to_print]:
        image_path= utils.make_fpath_from_id(_id, image_fldr)
        print(image_path)
        plot_image_from_fpath(image_path)
    
    return


def preprocess_img(image_path_or_stream):

    img = Image.open(image_path_or_stream)
    img = img.convert("RGB")
    size = 224, 224
    img = resize_image(img, size[0])
    img = img.resize(size, Image.ANTIALIAS)

    return img

 
def create_image_query_from_fpath(image_path):
    
    img = preprocess_img(image_path)
    img = np.array(img) /255
    x = tf.constant(img)
    x = tf.expand_dims(img, axis=0)
    return x


def test_an_id(test_id, image_fldr, retrieval_model, retrieval_exclusion_model, verbose=False):
      
    image_path = utils.make_fpath_from_id(test_id, image_fldr)
        
    print("query image path: ", image_path)
    plot_image_from_fpath(image_path)

    x = create_image_query_from_fpath(image_path)
    scores, identifiers = retrieval_model(x,k=15)
    id_list = identifiers.numpy()[0][:10]
    
    if verbose:
        print("retrieval_model results: ")
        print_list_of_ids(id_list, image_fldr)

    assert id_list[0] == test_id, "first returned result should be the query image's id"

    scores, identifiers = retrieval_exclusion_model(x,exclusions=identifiers,k=20)
    id_list_exc = identifiers.numpy()[0][:10]
    
    if verbose:
        print("retrieval_model_exclusion results: ")
        print_list_of_ids(id_list_exc, image_fldr)

    assert test_id not in id_list_exc, "test_id should not be in returned list when calling retrieval with exclusions" 
    return (id_list, id_list_exc)


def main():

    # should eventually be a call to the feature store with all features
    # fpath_feat = "../data/processed/ethz/features/features_prod.csv"
    # fpath_feat = "../data/processed/ethz/features/features_vgg16_imagenet.csv"
    fpath_feat = settings.interim_features_fpath
    df_feat = pd.read_csv(fpath_feat, header=None, index_col=0)

    # load the trained feature extraction model
    # fpath_model = "../models/feature_extraction/202109081606"
    fpath_model = settings.model_fldr_path
    ftx_model = tf.keras.models.load_model(fpath_model)

    # create the retrieval model
    retrieval_model = create_retrieval_model(query_model=ftx_model, 
                                            features=df_feat.values, 
                                            indentifiers=df_feat.index)
                                            
    # create the retireval exclusion model
    retrieval_exclusion_model = RetrievalExclusionModel(retrieval_model)
    retrieval_exclusion_model.compile()

    # test the models are basically functional (does not automatically check that they better!)

    image_fldr = settings.processed_image_dir  
    test_ids = [0,3,6,10]
    for test_id in test_ids:
        test_an_id(test_id,
                   image_fldr=settings.processed_image_dir,
                   retrieval_model=retrieval_model,
                   retrieval_exclusion_model=retrieval_exclusion_model)

    print(f"passed basic functionality test using images: {test_ids}")
    # save the retrieval model
    save_options = tf.saved_model.SaveOptions(namespace_whitelist=["Scann",])
    tf.saved_model.save(retrieval_model,"../models/retrieval/2", options=save_options)
    # save the retrieval exclusion model
    # if using scann, a custom op needs to be whitelisted
    save_options = tf.saved_model.SaveOptions(namespace_whitelist=["Scann",])
    retrieval_exclusion_model.save("../models/retrieval_exclusion/2",options=save_options)


if __name__ == '__main__':

    main()
