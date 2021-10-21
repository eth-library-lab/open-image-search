from rest_framework import status
from rest_framework.response import Response
import json
import numpy as np
import pandas as pd
from PIL import Image
import requests
from requests.exceptions import ConnectionError

from settings.settings import PREDICTION_MODEL_BASE_URL
from settings.settings import DEBUG, FAKE_MODEL_REPONSE
from ImageSearch.query_to_vector import load_filter_lookup, make_meta_vec, make_year_vec

FILTER_LOOKUP = load_filter_lookup()

class NumpyEncoder(json.JSONEncoder):
    """ Custom encoder for numpy data types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):

            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)): 
            return None

        return json.JSONEncoder.default(self, obj)

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
    img = img.resize(size, Image.ANTIALIAS)
    img = np.array(img)
    img = img / 255
    img = img.tolist()

    return img

 
def retrieve_top_ids(img_path_or_stream, qry_params):

    """
    send a request to the tensorflow serving container

    img_path_or_stream: image bytestream or filepath
    k: int, number of neighbours/results to return
    """
    qry_img = preprocess_img(img_path_or_stream)
    
    if len(qry_params)==0:
        meta_vec = None
        years_vec = None

    else:
        # look up using metadata and year vectors
        # create vectors from string query params
        meta_vec = make_meta_vec(FILTER_LOOKUP, **qry_params)
        years_vec = make_year_vec(**qry_params)

        # send to model
    
    # format request instance
    if (meta_vec is not None) and (years_vec is not None):
        model_name='retrieval_exclusion'
        request_dict = {"instances": [
                                {
                                "input_1":qry_img,
                                "input_2":meta_vec.tolist(),
                                "input_3":years_vec.tolist()
                                },
                            ]
                        }        

    else:
        model_name='retrieval'
        request_dict = {"instances":[
                                {
                                "input_1": qry_img,
                                },
                            ]
                        }
    # format full request
    model_url = f"{PREDICTION_MODEL_BASE_URL}/v1/models/{model_name}:predict"
    request_data = json.dumps(request_dict, cls=NumpyEncoder) 
    headers = {"content-type": "application/json"}

    if FAKE_MODEL_REPONSE and DEBUG:
        fake_resp = json.dumps({"predictions":[[4002, 4004, 4006, 4016, 4034],]})
        model_api_response = Response(status=200)
        model_api_response.text = fake_resp

    else:
        try:
            if DEBUG:
                print(f'sending request to model: {model_name}')

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
