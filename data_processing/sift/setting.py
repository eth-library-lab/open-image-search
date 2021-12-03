'''
SIFT and Vocabulary Tree Searching Model Settings  
'''

import os
import sys
from dotenv import load_dotenv

sys.path.append('../open-image-search/search-model/src')
load_dotenv("../open-image-search/search-model/.env.nbsettings")


################################################
#### Data Path ####
processed_image_dir = os.environ.get('PROCESSED_IMAGE_DIR','../open-image-search/search-model/data/processed/ethz/images')
img_path = '/25/25193.png'
query_img_path = processed_image_dir + img_path

database_image_dir = os.environ.get('CLAHE_IMAGE_DIR','../open-image-search/search-model/data/processed/ethz/images_clahe')


################################################
#### Vocabulary Tree ####

# number of children
C = 10
# number of levels
L = 6
# load pickle file of fitted graph
graph_path = f"data/grpah_C{C}L{L}.pickle"

################################################
#### RANSAC ####
num_candidates = 100