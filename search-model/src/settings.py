from pathlib import Path
import os
from dotenv import load_dotenv
import argparse

if os.environ.get("MODE") == "testing":
    load_dotenv("../.env.testing")
    

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# name for the collection of images. e.g. the instition's name 
dataset_name = os.environ.get("DATASET_NAME","test_set")

#### File Input and Output Settings ####
# run the preprocessing images pipeline to reseize,filter and save the raw images
preprocess_images = int(os.environ.get('PREPROCESS_IMAGES', 1))

###################################################################################################
#### File Input Settings ####

# provide path to directory of images OR path to a dataframe with filepath and identifier columns
#    directory of input images
raw_image_dir = os.environ.get('INPUT_IMAGE_DIR', f"data/raw/{dataset_name}/images")
raw_image_dir = os.path.join(BASE_DIR, raw_image_dir)

# (alternative) csv file that has a list of file paths to the image files
files_csv_fpath=None
filepath_col_name='img_path' # name of the column in the csv with the image filepaths
label_col_name='id' # name of the column in the csv with the unique id of the image

# specify the paths of metadata files separated by a space
metadata_csvs = os.environ.get("METADATA_CSVS", None)
if metadata_csvs:
    metadata_csvs = metadata_csvs.split(" ")
    metadata_csvs = [os.path.join(BASE_DIR, fpath) for fpath in metadata_csvs]

# directory of images to filter from the raw images set 
# (e.g. the image dataset contains a 'file not found' placeholder image)
removal_image_dir = os.environ.get("REMOVAL_IMAGE_DIR", f"data/raw/{dataset_name}/images_to_remove")
removal_image_dir = os.path.join(BASE_DIR, removal_image_dir)

###################################################################################################
#### File Output Settings ####

# directory of images to use to calculate features
processed_image_dir = os.environ.get("OUTPUT_IMAGE_DIR", f"data/processed/{dataset_name}/images")
processed_image_dir = os.path.join(BASE_DIR, processed_image_dir)


# output file for features
interim_features_fpath = os.path.join(BASE_DIR, 'data','interim', dataset_name,'features','features.csv')
processed_features_fpath = os.path.join(BASE_DIR, 'data','processed', dataset_name,'features','features.csv')

# interim output folder for cleaned metadata files
interim_metadata_dir = os.path.join(BASE_DIR, 'data','interim', dataset_name, 'metadata')
processed_metadata_dir = os.path.join(BASE_DIR, 'data','processed', dataset_name, 'metadata')
# output directory for fixtures
fixtures_dir = os.path.join(BASE_DIR, 'data','processed', dataset_name,'fixtures')

###################################################################################################
#### Feature Extraction Model Parameters ####

batch_size=32
model_name='vgg16_imagenet'
model_version="2"
weights='imagenet'
model_fldr_path=os.path.join(BASE_DIR,'models','feature_extraction', model_version)
calculate_features = int(os.environ.get("CALCULATE_FEATURES", 1))

###################################################################################################
#### Search Model Parameters ####

search_model_version="2"
search_model_fldr_path=os.path.join(BASE_DIR,'models','feature_extraction', search_model_version)
num_neighbours=int(os.environ.get("NUM_NEIGHBOURS", 10)) # number of results the search model should return
create_retrieval_model = int(os.environ.get("CREATE_RETRIEVAL_MODEL", 1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='settings file')
    parser.add_argument('--print', action='store_true',
                        help='print out main settings')
    args = parser.parse_args()

    if args.print:
        print("open imageSearch - Current Settings\n")
        print("DATASET NAME: ", dataset_name)
        print("BASE_DIR: ", BASE_DIR)
        print("\n----inputs----")
        print("list of metadata csvs: ")
        if metadata_csvs:
            for metadata_csv in metadata_csvs:
                print("    - ", metadata_csv)
        print("removal_image_dir: ", removal_image_dir)
        print("\n----outputs----")
        print("interim metadata dir (for cleaned metadata): ", interim_metadata_dir)
        print("fixtures output directory: ", fixtures_dir)

        print("\n---- Feature Extraction Model Parameters ----")
        calculate_features = int(os.environ.get("CALCULATE_FEATURES", 1))
        print("calculate_features: ", bool(calculate_features))
        print("\n---- Search Model Parameters ----")
        print("create_retrieval_model", bool(create_retrieval_model))