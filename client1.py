import base64
import cv2
import numpy as np
import requests

# read image
image = cv2.imread('0.jpg')
_, buffer = cv2.imencode('.jpg', image)
image_data = base64.b64encode(buffer).decode('utf-8')

# send HTTP POST request to API endpoint
url = 'http://127.0.0.1:5000/flip_image'
data = {'image': image_data}
response = requests.post(url, json=data)

# decode and display flipped image data
flipped_image_data = response.json()['flipped_image']
flipped_image_bytes = base64.b64decode(flipped_image_data)
flipped_image = cv2.imdecode(np.frombuffer(flipped_image_bytes, dtype=np.uint8), -1)

flipped_image = cv2.cvtColor(flipped_image, cv2.COLOR_BGR2RGB)

cv2.imshow('Flipped Image', flipped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()