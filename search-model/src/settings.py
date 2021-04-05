from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#### Feature Extration file and directory parameters ####
# provide path to directory of images OR path to a dataframe with filepath and identifier columns

# raw_image_dir=os.path.join(BASE_DIR, 'data','raw','ethz','images')
# processed_image_dir=os.path.join(BASE_DIR, 'data','processed','ethz','images')

preprocess_images = True
# directory of images to resize and save to processed directory
raw_image_dir=os.path.join(BASE_DIR, 'data','raw','eth_material_archive')
# directory of images to use to calculate features
processed_image_dir=os.path.join(BASE_DIR, 'data','processed','eth_material_archive')

files_csv_fpath=None
filepath_col_name='img_path'
label_col_name='object_id'

# specify the paths of metadata files from inside the data/raw folder
metadata_csvs_list = ['ethz/imageSearch_metadata_03.12.csv']

# output file for features
# features_fpath = os.path.join(BASE_DIR, 'data','processed','ethz','features.csv')
features_fpath = os.path.join(BASE_DIR, 'data','processed','eth_material_archive','features.csv')

# Model Parameters
batch_size=32
model_name='vgg16_imagenet'
model_version="2"
weights='imagenet'
model_fldr_path=os.path.join(BASE_DIR,'models','feature_extraction', model_version)

#Search Model Parameters
search_model_version="2"
search_model_fldr_path=os.path.join(BASE_DIR,'models','feature_extraction', search_model_version)
num_neighbours=10 # number of neighbours the model should return