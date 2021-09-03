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


def format_model_request(preprocessed_img):
    TENSORFLOW_SERVING_BASE_URL = "http://tf:8501/v1/models/model/versions/{model_version}:predict"
    model_url = TENSORFLOW_SERVING_BASE_URL.format(
                        model_name='feature_extraction',
                        model_version=202101182225,
                        )
    if DEBUG:
        print("TENSORFLOW_SERVING_BASE_URL", model_url)

    request_data = json.dumps({ "instances": [preprocessed_img, ]}) 
    headers = {"content-type": "application/json"}

    return model_url, request_data, headers


def post_to_model(preprocessed_img):
    
    request_params = format_model_request(preprocessed_img)
    model_url, request_data, headers = request_params

    if DEBUG:
        print('model_url: ', model_url)
        print('headers: ', headers)
        print('request_data: ', str(request_data)[:100],' ...')

    model_api_response = requests.post(model_url, 
                                        data=request_data, 
                                        headers=headers)

    if DEBUG:
        print('model_api_response: ', model_api_response)
    
    return model_api_response


def calculate_image_features(img_path_or_stream):
    """
    send a request to the feature extraction model and return the image feature vector"
    """
    preprocessed_img = preprocess_img(img_path_or_stream)    
    model_response = post_to_model(preprocessed_img)

    if DEBUG:
        print('model_response: ', model_response.status_code)

    if model_response.status_code != 200:
        return Response(model_response.content, model_response.status_code)
    
    model_response_dict = json.loads(model_response.text)

    if DEBUG:
        print('model_response_dict', model_response_dict)

    model_raw_values = model_response_dict['predictions'][0]
    image_features = np.array(model_raw_values).reshape(1, -1) # reshape for a single record
    
    return image_features

