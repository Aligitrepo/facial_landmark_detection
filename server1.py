from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np
import itertools
import numpy as np
from time import time
import mediapipe as mp
import matplotlib.pyplot as plt

def my_medipipe_func(image):
    # Initialize the mediapipe face detection class.
    mp_face_detection = mp.solutions.face_detection

    # Setup the face detection function.
    face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

    # Initialize the mediapipe drawing class.
    mp_drawing = mp.solutions.drawing_utils

    # Perform face detection after converting the image into RGB format.
    face_detection_results = face_detection.process(image[:, :, ::-1])

    img_detect = image[:, :, ::-1].copy()

    # Check if the face(s) in the image are found.
    if face_detection_results.detections:

        # Iterate over the found faces.
        for face_no, face in enumerate(face_detection_results.detections):
            # Draw the face bounding box and key points on the copy of the sample image.
            mp_drawing.draw_detection(image=img_detect, detection=face,
                                      keypoint_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0),
                                                                                   thickness=2,
                                                                                   circle_radius=2))
    return img_detect



app = Flask(__name__)


# when a client sends a POST request to the URL path /flip_image of the Flask application, the flip_image() function will be executed.
@app.route('/flip_image', methods=['POST'])
def flip_image():
    # get image data from request
    image_data = request.json['image']

    # convert image data to numpy array
    image_bytes = base64.b64decode(image_data)
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), -1)

    # flip image horizontally
    flipped_image = cv2.flip(image, 1)

    # convert flipped image to base64 encoded string
    retval, buffer = cv2.imencode('.jpg', flipped_image)
    flipped_image_data = base64.b64encode(buffer).decode('utf-8')

    # return flipped image to app
    return jsonify({'flipped_image': flipped_image_data})

@app.route('/face_detect', methods=['POST'])
def face_detect():
    # get image data from request
    image_data = request.json['image']

    # convert image data to numpy array
    image_bytes = base64.b64decode(image_data)
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), -1)

    # blur image
    blurred_image = my_medipipe_func(image)

    # convert blurred image to base64 encoded string
    retval, buffer = cv2.imencode('.jpg', blurred_image)
    blurred_image_data = base64.b64encode(buffer).decode('utf-8')

    # return blurred image to app
    return jsonify({'blurred_image': blurred_image_data})



if __name__ == '__main__':
    app.run(debug=True)
