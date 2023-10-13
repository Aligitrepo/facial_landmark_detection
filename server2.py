import base64
import os
import cv2
import numpy as np
from flask import Flask, request, jsonify


app = Flask(__name__)
# define image ID to image file name mapping
id_to_file = {'1': '0.jpg', '2': '0.jpg'}

@app.route('/get_image_data', methods=['POST'])
def get_image_data():
    # get the ID from the request
    image_id = request.json['id']

    # check if ID is valid and image file exists
    if image_id in id_to_file:
        image_file = id_to_file[image_id]
        if not os.path.isfile(image_file):
            return jsonify({'error': 'Image file not found'})

        # if valid, read the image file and encode it as base64
        image = cv2.imread(image_file)
        _, buffer = cv2.imencode('.jpg', image)
        image_data_encoded = base64.b64encode(buffer).decode('utf-8')
        image_name = "Elon MUSK"
        image_description = "Hi, Want to go to Mars?"

        return jsonify({'image_data': image_data_encoded, 'name': image_name, 'description': image_description})

    else:
        return jsonify({'error': 'Invalid image ID'})

if __name__ == '__main__':
    app.run(debug=True)
