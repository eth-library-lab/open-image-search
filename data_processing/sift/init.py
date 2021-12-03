import numpy as np
import pandas as pd
import networkx as nx
import os
import sys

sys.path.append('../open-image-search/search-model/src')
from utils import get_list_of_files_in_dir
from SIFT import create_dict_of_img_by_id
from query_vocabulary_tree import img_process, create_lookup_df, propagate_query, get_similar_imgs, filter_by_ransca, create_dict_of_des_by_id
import setting


def main():
    #get path for query image
    query_img_path = setting.query_img_path

    # apply CLAHE on query image and extract SIFT features
    des1 = img_process(query_img_path)
    (_, features) = des1 

    # propagate features from query image 
    leaf_id_results = propagate_query(G,features)
    # get the score for each image in the database
    df_counts_sums = get_similar_imgs(df_lookup, leaf_id_results)
    # run RANSAC for geometric verification
    match_count_dic = filter_by_ransca(des1, df_counts_sums, des_dic, setting.num_candidates)

    print(match_count_dic)
    return match_count_dic


if __name__ == '__main__':
    # get file pathes of database
    search_fpaths_input = get_list_of_files_in_dir(setting.database_image_dir, file_types = ['jpg', 'jpeg','png','bmp'])
    # N: number of images in the database
    N = len(search_fpaths_input)

    des_dic = create_dict_of_des_by_id(search_fpaths_input)

    # load pickle file of fitted graph
    G = nx.read_gpickle(setting.graph_path)
    # create lookup dataframe
    df_lookup = create_lookup_df(G, N)

    main()

