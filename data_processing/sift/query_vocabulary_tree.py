import numpy as np
import pandas as pd

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import cv2
import matplotlib.pyplot as plt
import pickle
import networkx as nx
from tqdm import tqdm

sys.path.append('../open-image-search/search-model/src')
load_dotenv("./.env.nbsettings")
    
from utils import get_list_of_files_in_dir
from vocabulary import VocabularyTree
from SIFT import ransac_filter, match_sift_ransac, compute_sift, create_img_id, create_dict_of_des_by_id, create_dict_of_img_by_id


def img_process(query_img_path):
    '''
    apply CLAHE on query image and extract SIFT features

    return:
    tuple of (kp,des)
    kp: keypoints indices
    des: descriptors with dimension num_of_keypoints*128
    '''
    img = cv2.imread(query_img_path, 0)
    clahe = cv2.createCLAHE(clipLimit = 5, tileGridSize=(8, 8))
    clahe_img = clahe.apply(img)

    
    des1= compute_sift(clahe_img, rootsift = True)

    return des1


def create_lookup_df(G, N):
    '''
    return a lookup dataframe with columns of leaf_id, img_id, n, num_image_in_leaf, idf
    '''
    # get leaf ids from voc. iterates over nodes. is a leaf if there are no child edges out of that node
    leaf_ids = [n for n in G.nodes.keys() if 0 == G.graph.out_degree(n)]
    
    # create a lookup array for leaf_id - img_id - counts
    arr = np.array([[]])
    arr_all = []

    for leaf_id in leaf_ids:
        leaf_items = G.graph.nodes[leaf_id].items()
        if len(leaf_items) != 0:
            arr = np.array(list(leaf_items), dtype="O")
            ids = np.ones(arr.shape[0], dtype=int) * leaf_id

            try:
                arr = np.hstack([np.expand_dims(ids.astype(str), axis=1), arr])
            except:
                print(np.expand_dims(ids.astype(str), axis=1))
                print(arr)
                break
            arr_all.append(arr)

    
    arr_all = np.vstack(arr_all)
    
    # convert into dataframe  
    df_lookup = pd.DataFrame(arr_all, columns=['leaf_id', 'img_id', 'n'])
    df_lookup["leaf_id"] = df_lookup["leaf_id"].astype(str)
    df_lookup["img_id"] = df_lookup["img_id"].astype(str)
    df_lookup["n"] = pd.to_numeric(df_lookup["n"])
    
    df_lookup['num_image_in_leaf'] = df_lookup['leaf_id'].map(df_lookup['leaf_id'].value_counts())
    df_lookup['idf'] = float(N)/(df_lookup['num_image_in_leaf'])
    
    return df_lookup


def propagate_query(G,features):
    '''
    get leaf nodes for query image features

    return a list of leaf ids for the query features
    ''' 
    leaf_id_results = []

    for des in features:
        path = G.propagate_feature(des)
        leaf_id_results.append(str(path[-1]))
    
    return leaf_id_results


def get_similar_imgs(df_lookup, leaf_id_results):
    '''
    get the score for each image in the database

    return:
    sorted dataframe with columns of image id(img_id) and tf-idf score(norm_cnt), highest scores at the top
    '''
    # from the array of counts, select only the visual words that occur in the query image 
    df_counts = df_lookup[df_lookup['leaf_id'].isin(leaf_id_results)].copy()
    df_counts['norm_cnt'] = df_counts['n']*np.log(df_counts['idf'])

    # group counts by img_id and sort decendingly
    df_counts_group = df_counts[["img_id",'norm_cnt']].groupby(['img_id'],as_index=False).sum()
    df_counts_sums = df_counts_group.sort_values(by='norm_cnt', ascending=False)
    
    return df_counts_sums


def filter_by_ransca_old(query_features, df_counts_sums, img_dic, n):
    '''
    run RANSAC for geometric verification

    return:
    dictionary of point match counts by image id, sorted in decending order
    '''

    cnt_by_id = {}
    for i in range(n):
        img_id = df_counts_sums.iloc[i]['img_id']
        img_arrary = img_dic.get(img_id)
        des2 = compute_sift(img_arrary, rootsift = True)  
        match_cnt = ransac_filter(query_features, des2, thre = 20)
        cnt_by_id[str(img_id)] = match_cnt
    return dict(sorted(cnt_by_id.items(), key=lambda item: item[1], reverse=True)) 

def filter_by_ransca(query_features, df_counts_sums, des_dic, n):
    '''
    run RANSAC for geometric verification

    return:
    dictionary of point match counts by image id, sorted in decending order
    '''

    cnt_by_id = {}
    for i in range(n):
        # query descriptors for candidaite images
        img_id = df_counts_sums.iloc[i]['img_id']
        feat_list = des_dic.get(img_id)
        # transform array back to keypoint type
        keypoint = [cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], 
                            _response=point[3], _octave=point[4], _class_id=point[5]) for point in feat_list]
        des = np.array([point[6] for point in feat_list])

        match_cnt = ransac_filter(query_features, (keypoint, des), thre = 20)
        cnt_by_id[str(img_id)] = match_cnt
    return dict(sorted(cnt_by_id.items(), key=lambda item: item[1], reverse=True)) 