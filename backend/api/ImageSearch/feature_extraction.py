from rest_framework import status
from rest_framework.response import Response
# from settings.settings import TENSORFLOW_SERVING_BASE_URL 
from settings.settings import DEBUG

import json
import numpy as np
import pandas as pd
from PIL import Image
import requests

######################################

from settings.settings import BASE_DIR
import os

def calc_resize_with_apect(size, min_dimension):
    
    w = size[0]
    h = size[1]
        
    # if min(size) > min_dimension:

    new_w = (w / min(size)) * min_dimension
    new_h = (h / min(size)) * min_dimension
        
    new_size = (int(new_w), int(new_h))

    return new_size


def resize_image(pil_image, min_dimension):
    
    """resize a pil image to have the minimum dimension given on oneside"""
    
    new_size = calc_resize_with_apect(pil_image.size, min_dimension=min_dimension)  
    pil_image = pil_image.resize(new_size, resample = Image.ANTIALIAS)
    
    return pil_image


def preprocess_img(image_path_or_stream):

    img = Image.open(image_path_or_stream)
    img = img.convert("RGB")
    size = 224, 224
    img = resize_image(img, size[0])
    if DEBUG:
        print('np array shape: ', np.array(img).shape)
    img = img.resize(size, Image.ANTIALIAS)
    img = np.array(img)
    if DEBUG:
        print('np array shape: ', img.shape)
    img = img / 255
    img = img.tolist()

    return img


def format_model_request(preprocessed_img, model_name, function_name='predict'):
    TENSORFLOW_SERVING_BASE_URL = "http://tf:8501/v1/models/{model_name}:{function_name}"
    model_url = TENSORFLOW_SERVING_BASE_URL.format( 
                        model_name=model_name,,
                        function_name=function_name
                        )
    request_data = json.dumps({ "instances": [preprocessed_img, ]}) 
    headers = {"content-type": "application/json"}

    return model_url, request_data, headers


def request_top_ids(img_path_or_stream, ids_to_exclude=None, k=10):

    preprocessed_img = preprocess_img(img_path_or_stream)

    if ids_to_exclude:
        model_name='retrieval_exclusion'
        model_url = f"http://tf:8501/v1/models/{model_name}:predict"
        request_dict = {
            "instances": [
                {
                    "queries": preprocessed_img,
                    "exclusions": list(ids_to_excludes),
                    "k":k
                },
            ]
        }
        
    else:
        model_name='retrieval'
        model_url = f"http://tf:8501/v1/models/{model_name}:predict"
        request_dict = {
            "instances": [
                {
                    "queries": preprocessed_img,
                    "k":k
                },
            ]
        }

    request_data = json.dumps(request_dict) 
    headers = {"content-type": "application/json"}
    model_api_response = requests.post(model_url, 
                                        data=request_data, 
                                        headers=headers)
    return model_api_response


# def calculate_image_features(img_path_or_stream):
#     """
#     send a request to the feature extraction model and return the image feature vector"
#     """
       
#     model_response = post_to_model(preprocessed_img)


