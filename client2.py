import base64
import cv2
import numpy as np
import requests

# define the unique id
id = '1'

# send HTTP POST request to API endpoint
url = 'http://127.0.0.1:5000/get_image_data'
data = {'id': id}
response = requests.post(url, json=data)

# check for errors in the response
if 'error' in response.json():
    print(response.json()['error'])
else:
    # get image data and metadata from server response
    image_data_encoded = response.json()['image_data']
    name = response.json()['name']
    description = response.json()['description']

    # decode and display image data
    image_bytes = base64.b64decode(image_data_encoded)
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), -1)
    cv2.imshow(name, image)
    print('Name:', name)
    print('Description:', description)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
