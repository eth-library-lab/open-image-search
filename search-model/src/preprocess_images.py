#!/usr/bin/env python
# coding: utf-8 

from PIL import Image
import os
import numpy as np
import utils
import settings

def calc_resize_with_apect(size, min_dimension):
    """calculate the dimensions needed to resize an image with the minimum dimension on one side
    while preserving the aspect ratio.
    size: tuple containing the original image size in pixels (w,h)
    min_dimension: min pixel size on one size
    """
    w = size[0]
    h = size[1]

    new_w = (w / min(size)) * min_dimension
    new_h = (h / min(size)) * min_dimension

    new_size = (int(new_w), int(new_h))

    return new_size


def resize_image(pil_image, min_dimension=224):
    """resize a pil image to have the minimum dimension given on oneside"""
    
    new_size = calc_resize_with_apect(pil_image.size, min_dimension=min_dimension)  
    pil_image = pil_image.resize(new_size, resample = Image.ANTIALIAS)
    
    return pil_image


def preprocess_image(input_img_path, output_img_path, min_dimension=224): 
    """open an image from a file path, resize it and save"""
    img = Image.open(input_img_path)
    img = resize_image(img, min_dimension)
    img.save(output_img_path)
    
    return


def get_list_of_img_fpaths_to_process(input_image_dir, output_image_dir, keep_fldr_path=False):
    """
    get list of images in input_image_dir. remove fpaths from list if they
    are already in the output_image_dir
    """

    print('checking input directory: {}'.format(input_image_dir))
    existing_fpaths_input = utils.get_list_of_files_in_dir(input_image_dir, file_types = ['jpg', 'jpeg','png'], keep_fldr_path=keep_fldr_path)
    print('checking output directory: {}'.format(output_image_dir)) 
    existing_fpaths_output = utils.get_list_of_files_in_dir(output_image_dir, file_types = ['jpg', 'jpeg','png'],keep_fldr_path=keep_fldr_path)
    
    existing_fnames_output = [os.path.split(f)[1] for f in existing_fpaths_output]
    fpaths_to_process = [f for f in existing_fpaths_input if os.path.split(f)[1] not in existing_fnames_output]    

    return fpaths_to_process


def calc_print_status_interval(num_images_to_proc):
    """calculate number of iterations to run between printing a status output
    at each 10% progress interval or every 1000 images
    num_images_to_proc"""
    
    print_interval = min(max(1, int(num_images_to_proc/10)), 1000)    
    return print_interval


def print_status_if_at_inteval(num_images_to_proc, print_interval, current_step):
    """print a status update at the calculated steps or when processing the last image"""

    if (((current_step+1) % print_interval) == 0) or ((current_step+1) == num_images_to_proc):
        print("finished processing {:,} of {:,} images".format(current_step+1, num_images_to_proc))
    
    return


def process_dir_of_images(input_image_dir, output_image_dir):
    """
    apply the processing pipeline to a directory of images and save them to the output_image_directory
    """
    
    fpaths_to_process = get_list_of_img_fpaths_to_process(input_image_dir, output_image_dir, keep_fldr_path=True)
    num_images_to_proc = len(fpaths_to_process)
    print('num images to process {:,}'.format(num_images_to_proc))
    
    print_interval = calc_print_status_interval(num_images_to_proc)
    
    # loop over each file path and save the processed image output
    for i, input_img_path in enumerate(fpaths_to_process):

        # make_output_fpath
        output_subpath = input_img_path.replace(input_image_dir,'').strip('\\').strip('/')
        output_img_path = os.path.join(output_image_dir, output_subpath)
        
        #it the output filepath already exists skip to the next image
        if os.path.exists(output_img_path):
            print('    info:image already exists {}'.format(output_img_path))
            continue

        # make the output folder if it does not already exist
        output_fldr_path = os.path.dirname(output_img_path)
        if not os.path.exists(output_fldr_path):
            print('making output_fldr_path: ', output_fldr_path)
            os.makedirs(output_fldr_path)

        #load, process and save altered image
        try:
            preprocess_image(input_img_path, output_img_path, min_dimension=224)
        except FileNotFoundError as e:
            print("    warning: could not preprocess image {}".format(input_img_path))
            print("    ", e)
        
        # print_status_if_at_inteval(num_images_to_proc, print_interval, i)
        utils.print_dyn_progress_bar(num_images_to_proc, i)
    return


def main():

    input_dir = settings.raw_image_dir 
    output_dir = settings.processed_image_dir

    process_dir_of_images(input_dir, output_dir)

    return

if __name__ == '__main__':

    main()