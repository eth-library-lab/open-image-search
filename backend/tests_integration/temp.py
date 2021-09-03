import requests
from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import json
import os

api_host = "http://localhost:8000/api"



img_path = "../../search-model/data/processed/ethz/images/0/3.png"
img = image.load_img(img_path, target_size=(224, 224))
# x = image.img_to_array(img)
# x = np.expand_dims(x, axis=0)
# x = preprocess_input(x)

# headers = {"content-type": "multipart/form-data"}
# data = json.dumps({"image": img})
url = "http://127.0.0.1:8000/api/image-search"

with open(img_path, 'rb') as img:
    files = {
            'image': (os.path.basename(img_path), img),
            'Content-Type': 'image/jpeg',
        }
    json_response = requests.post(url, files=files)

# json_response = requests.post(url,
#                               data=data,
#                               headers=headers)

print('response status:', json_response.status_code)
if json_response.status_code == 200:
    print('ok')


    predictions = json.loads(json_response.text)
    print(predictions)
