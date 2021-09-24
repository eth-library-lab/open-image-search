from rest_framework import status
from rest_framework.response import Response
# from settings.settings import TENSORFLOW_SERVING_BASE_URL 
from settings.settings import DEBUG, FAKE_MODEL_REPONSE

import json
import numpy as np
import pandas as pd
from PIL import Image
import requests
from requests.exceptions import ConnectionError
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
                        model_name=model_name,
                        function_name=function_name
                        )
    request_data = json.dumps({ "instances": [preprocessed_img, ]}) 
    headers = {"content-type": "application/json"}

    return model_url, request_data, headers


def request_top_ids(img_path_or_stream, ids_to_exclude=None, k=10):

    """
    img_path_or_stream: image bytestream or filepath
    ids_to_exclude: identifiers to exclude from the top results
    k:int, number of neighbours/results to return
    """
    preprocessed_img = preprocess_img(img_path_or_stream)

    # format request instance
    if ids_to_exclude:
        print("ids_to_exclude:", ids_to_exclude)
        model_name='retrieval_exclusion'
        input = {"args_0": [preprocessed_img,],
                 "args_1": [list(ids_to_exclude),],
                 "args_2":[k,],}
    else:
        model_name='retrieval'
        input = {"input_1": [preprocessed_img,],
                 "input_2":[k,],}

    
    # format full request
    request_dict = {"inputs": input}
    model_url = f"http://tf:8501/v1/models/{model_name}:predict"
    
    if DEBUG:
        print(f'sending request to model: {model_name}')

    request_data = json.dumps(request_dict) 
    headers = {"content-type": "application/json"}

    if FAKE_MODEL_REPONSE and DEBUG:
        fake_resp = json.dumps({"predictions":[[4002, 4004, 4006, 4016, 4034],]})
        model_api_response = Response(status=200)
        model_api_response.text = fake_resp

    else:
        try:
            model_api_response = requests.post(model_url, 
                                                data=request_data, 
                                                headers=headers)
        except ConnectionError as err:
            err_message = "feature extraction model ConnectionError"
            model_api_response = Response({"error": err_message}, status=500)
            model_api_response.text = err_message

        except Exception as err:
            err_message = "feature extraction model error"
            model_api_response = Response({"error": err_message}, status=500)
            model_api_response.text = err_message

    return model_api_response


