import requests

from PIL import Image
import numpy as np
import json
import os
from pprint import pprint

api_host = "http://localhost:8000/api"

img_path = "../../search-model/data/processed/ethz/images/220/220526.png"
img = Image.open(img_path)
# x = image.img_to_array(img)
# x = np.expand_dims(x, axis=0)
# x = preprocess_input(x)

# headers = {"content-type": "multipart/form-data"}
# data = json.dumps({"image": img})
url = "http://127.0.0.1:8000/api/image-search"
qry= "?" 
qry += "&" + "afterYear=1750"
qry += "&" + "beforeYear=1770"
# qry += "&" + "classification=Buch"
# qry += "&" + "classification=Buch"
# qry += "&" + "materialTechnique=radierung"
url = url + qry
with open(img_path, 'rb') as img:
    files = {
            'image': (os.path.basename(img_path), img),
            'Content-Type': 'image/jpeg',
        }
    response = requests.post(url, files=files)


print('response status:', response.status_code)
if response.status_code == 200:
    print('ok')


    predictions = json.loads(response.text)
    pprint(predictions, indent=2)
else:
    print("response.text: ", response.text)
print('\n',url)

