import pandas as pd
import numpy as np
import shutil
import os,sys

sys.path.append("../src")

import utils

def rand_sample_of_df(df, num_records=100):
    """
    get a random subsample(without replacement) of a dataframe
    """ 
    np.random.seed(42)
    test_indices = np.random.choice(df.index, replace=False, size=num_records)
    df_test = df.loc[test_indices,:]
    
    return df_test


def copy_selection_of_files(input_file_dir, output_file_dir, files_to_copy):
    """
    find the given list of image names in the input directory and copy them to the output directory
    """ 
    # find images in directory 
    for dirpath, dirnames, filenames in os.walk(input_file_dir):
        for fname in filenames:
            if fname in files_to_copy:
                cur_fpath = os.path.join(dirpath, fname)            
                dest = cur_fpath.replace(input_file_dir, output_file_dir)
                utils.prep_dir(dest)
                shutil.copy2(cur_fpath, dest)
    return


def add_images_to_remove(input_file_dir, output_file_dir, num_images=3):
    """
    to test that image removal/filtering function works,
    copy files to the the images_to_remove folder
    """ 
    i=0

    for dirpath, dirnames, filenames in os.walk(input_file_dir):
        for fname in filenames:
            cur_fpath = os.path.join(dirpath, fname)
            dest = os.path.join(output_file_dir, "images_to_remove", fname) 
            utils.prep_dir(dest)
            shutil.copy2(cur_fpath, dest)
            i+=1
            if i >= num_images:
                return


def main(num_records=100):
    """
    create a randomly selected test dataset of the given size 
    """

    # load metadata csv to sample from
    input_dir_path = "../data/raw/ethz"
    input_fpath = os.path.join(input_dir_path, "metadata/imageSearch_metadata_03.12.csv")
    df = pd.read_csv(input_fpath)

    # output directory path
    test_dirpath = "../data/raw/test_set"
    output_fpath = os.path.join(test_dirpath, "metadata/metadata.csv")

    # subsample the df
    df_test = rand_sample_of_df(df, num_records=num_records)
    
    # write out sample dataframe
    fpath = utils.prep_dir(output_fpath)
    df_test.to_csv(output_fpath, index=False)

    # make a list of images to copy
    images_to_copy = df_test['recordID'].astype(str) + '.png'
    images_to_copy = images_to_copy.to_list()

    # copy images into test folder
    test_image_dir = os.path.join(test_dirpath, "images")
    copy_selection_of_files(input_dir_path, test_image_dir, images_to_copy)
    
    print(f"saved test dataset of {num_records} records from  {input_dir_path}  to  {test_dirpath}")
    return


if __name__ == "__main__":

    main(num_records=100)