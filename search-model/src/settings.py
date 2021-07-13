from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# name for the collection of images. e.g. the instition's name 
dataset_name = os.environ.get("DATASET_NAME","test_set")

#### File Input and Output Settings ####
# run the preprocessing images pipeline to reseize,filter and save the raw images
preprocess_images = os.environ.get('PREPROCESS_IMAGES', True)

### provide path to directory of images OR path to a dataframe with filepath and identifier columns
# directory of input images
raw_image_dir = os.environ.get('INPUT_IMAGE_DIR', f"data/raw/{dataset_name}/images")
raw_image_dir = os.path.join(BASE_DIR, raw_image_dir)

## OR

#specify a csv file that has a list of file paths to the image files
files_csv_fpath=None
filepath_col_name='img_path' # name of the column in the csv with the image filepaths
label_col_name='object_id' # name of the column in the csv with the unique id of the image

# directory of images to use to calculate features
processed_image_dir = os.environ.get("OUTPUT_IMAGE_DIR", f"data/processed/{dataset_name}/images")
processed_image_dir = os.path.join(BASE_DIR, processed_image_dir)

# directory of images to filter from the raw images set (e.g. if the image dataset contains a 'file not found' placeholder image)
removal_image_dir = os.environ.get("REMOVAL_IMAGE_DIR", f"data/raw/{dataset_name}/images_to_remove")
removal_image_dir = os.path.join(BASE_DIR, removal_image_dir)

# specify the paths of metadata files separated by a space
metadata_csvs = os.environ.get("METADATA_CSVS", f"data/raw/{dataset_name}/imageSearch_metadata_03.12.csv")
metadata_csvs = metadata_csvs.split(" ")
metadata_csvs = [os.path.join(BASE_DIR, fpath) for fpath in metadata_csvs]

# output file for features
features_fpath = os.path.join(BASE_DIR, 'data','processed', dataset_name, 'features.csv')

# Model Parameters
batch_size=32
model_name='vgg16_imagenet'
model_version="2"
weights='imagenet'
model_fldr_path=os.path.join(BASE_DIR,'models','feature_extraction', model_version)

#Search Model Parameters
search_model_version="2"
search_model_fldr_path=os.path.join(BASE_DIR,'models','feature_extraction', search_model_version)
num_neighbours=os.environ.get("NUM_NEIGHBOURS", 10) # number of results the search model should return