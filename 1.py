import cv2
import itertools
import numpy as np
from time import time
import mediapipe as mp
import matplotlib.pyplot as plt

# Initialize the mediapipe face detection class.
mp_face_detection = mp.solutions.face_detection

# Setup the face detection function.
# face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# Initialize the mediapipe drawing class.
mp_drawing = mp.solutions.drawing_utils

# Perform face detection after converting the image into RGB format.
# face_detection_results = face_detection.process(sample_img[:, :, ::-1])

# Initialize the mediapipe face mesh class.
mp_face_mesh = mp.solutions.face_mesh

# Setup the face landmarks function for images.
face_mesh_images = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=2,
                                         min_detection_confidence=0.5)

# # Setup the face landmarks function for videos.
# face_mesh_videos = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1,
#                                          min_detection_confidence=0.5,min_tracking_confidence=0.3)

# Initialize the mediapipe drawing styles class.
mp_drawing_styles = mp.solutions.drawing_styles

def detectFacialLandmarks(image, face_mesh, display = True):

    # Perform the facial landmarks detection on the image, after converting it into RGB format.
    results = face_mesh.process(image[: ,: ,::-1])

    # Create a copy of the input image to draw facial landmarks.
    output_image = image[: ,: ,::-1].copy()

    # Check if facial landmarks in the image are found.
    if results.multi_face_landmarks:

        # Iterate over the found faces.
        for face_landmarks in results.multi_face_landmarks:

            # Draw the facial landmarks on the output image with the face mesh tesselation
            # connections using default face mesh tesselation style.
            mp_drawing.draw_landmarks(image=output_image, landmark_list=face_landmarks,
                                      connections=mp_face_mesh.FACEMESH_TESSELATION,
                                      landmark_drawing_spec=None,
                                      connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

            # Draw the facial landmarks on the output image with the face mesh contours
            # connections using default face mesh contours style.
            mp_drawing.draw_landmarks(image=output_image, landmark_list=face_landmarks,
                                      connections=mp_face_mesh.FACEMESH_CONTOURS,
                                      landmark_drawing_spec=None,
                                      connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())

    # Check if the original input image and the output image are specified to be displayed.
    if display:

        # Display the original input image and the output image.
        plt.figure(figsize=[15 ,15])
        plt.subplot(121)
        plt.imshow(image[: ,: ,::-1])
        plt.title("Original Image")
        plt.axis('off');
        plt.subplot(122)
        plt.imshow(output_image)
        plt.title("Output")
        plt.axis('off');

    # Otherwise
    else:

        # Return the output image in BGR format and results of facial landmarks detection.
        return np.ascontiguousarray(output_image[: ,: ,::-1], dtype=np.uint8), results


image = cv2.imread('0.jpg')
# detectFacialLandmarks(image, face_mesh_images, display=True)

def getSize(image, face_landmarks, INDEXES):
    '''
    This function calculate the height and width of a face part utilizing its landmarks.
    Args:
        image:          The image of person(s) whose face part size is to be calculated.
        face_landmarks: The detected face landmarks of the person whose face part size is to
                        be calculated.
        INDEXES:        The indexes of the face part landmarks, whose size is to be calculated.
    Returns:
        width:     The calculated width of the face part of the face whose landmarks were passed.
        height:    The calculated height of the face part of the face whose landmarks were passed.
        landmarks: An array of landmarks of the face part whose size is calculated.
    '''

    # Retrieve the height and width of the image.
    image_height, image_width, _ = image.shape

    # Convert the indexes of the landmarks of the face part into a list.
    INDEXES_LIST = list(itertools.chain(*INDEXES))

    # Initialize a list to store the landmarks of the face part.
    landmarks = []

    # Iterate over the indexes of the landmarks of the face part.
    for INDEX in INDEXES_LIST:
        # Append the landmark into the list.
        landmarks.append([int(face_landmarks.landmark[INDEX].x * image_width),
                          int(face_landmarks.landmark[INDEX].y * image_height)])

    # Calculate the width and height of the face part.
    _, _, width, height = cv2.boundingRect(np.array(landmarks))

    # Convert the list of landmarks of the face part into a numpy array.
    landmarks = np.array(landmarks)

    # Retrurn the calculated width height and the landmarks of the face part.
    return width, height, landmarks


def isOpen(image, face_mesh_results, face_part, threshold=5, display=True):
    '''
    This function checks whether the an eye or mouth of the person(s) is open,
    utilizing its facial landmarks.
    Args:
        image:             The image of person(s) whose an eye or mouth is to be checked.
        face_mesh_results: The output of the facial landmarks detection on the image.
        face_part:         The name of the face part that is required to check.
        threshold:         The threshold value used to check the isOpen condition.
        display:           A boolean value that is if set to true the function displays
                           the output image and returns nothing.
    Returns:
        output_image: The image of the person with the face part is opened  or not status written.
        status:       A dictionary containing isOpen statuses of the face part of all the
                      detected faces.
    '''

    # Retrieve the height and width of the image.
    image_height, image_width, _ = image.shape

    # Create a copy of the input image to write the isOpen status.
    output_image = image.copy()

    # Create a dictionary to store the isOpen status of the face part of all the detected faces.
    status = {}

    # Check if the face part is mouth.
    if face_part == 'MOUTH':

        # Get the indexes of the mouth.
        INDEXES = mp_face_mesh.FACEMESH_LIPS

        # Specify the location to write the is mouth open status.
        loc = (10, image_height - image_height // 40)

        # Initialize a increment that will be added to the status writing location,
        # so that the statuses of two faces donot overlap.
        increment = -30

    # Check if the face part is left eye.
    elif face_part == 'LEFT EYE':

        # Get the indexes of the left eye.
        INDEXES = mp_face_mesh.FACEMESH_LEFT_EYE

        # Specify the location to write the is left eye open status.
        loc = (10, 30)

        # Initialize a increment that will be added to the status writing location,
        # so that the statuses of two faces donot overlap.
        increment = 30

    # Check if the face part is right eye.
    elif face_part == 'RIGHT EYE':

        # Get the indexes of the right eye.
        INDEXES = mp_face_mesh.FACEMESH_RIGHT_EYE

        # Specify the location to write the is right eye open status.
        loc = (image_width - 300, 30)

        # Initialize a increment that will be added to the status writing location,
        # so that the statuses of two faces donot overlap.
        increment = 30

    # Otherwise return nothing.
    else:
        return

    # Iterate over the found faces.
    for face_no, face_landmarks in enumerate(face_mesh_results.multi_face_landmarks):

        # Get the height of the face part.
        _, height, _ = getSize(image, face_landmarks, INDEXES)

        # Get the height of the whole face.
        _, face_height, _ = getSize(image, face_landmarks, mp_face_mesh.FACEMESH_FACE_OVAL)

        # Check if the face part is open.
        if (height/face_height)*100 > threshold:

            # Set status of the face part to open.
            status[face_no] = 'OPEN'

            # Set color which will be used to write the status to green.
            color = (0, 255, 0)

        # Otherwise.
        else:
            # Set status of the face part to close.
            status[face_no] = 'CLOSE'

            # Set color which will be used to write the status to red.
            color = (0, 0, 255)

        # Write the face part isOpen status on the output image at the appropriate location.
        cv2.putText(output_image, f'FACE {face_no + 1} {face_part} {status[face_no]}.',
                    (loc[0], loc[1] + (face_no * increment)), cv2.FONT_HERSHEY_PLAIN, 1.4, color, 2)

    # # Check if the output image is specified to be displayed.
    # if display:

        # Display the output image.
    plt.figure(figsize=[10, 10])
    plt.imshow(output_image[:, :, ::-1]);
    plt.title("Output Image");
    plt.axis('off');
    cv2.imshow("1", output_image)

    # Otherwise
    # else:

        # Return the output image and the isOpen statuses of the face part of each detected face.
    return output_image, status



# Read another sample image and perform facial expression recognition on it.
image = cv2.imread('0.jpg')
cv2.imshow("2", image)
image = cv2.flip(image, 1)
_, face_mesh_results = detectFacialLandmarks(image, face_mesh_images, display=False)
if face_mesh_results.multi_face_landmarks:
    cv2.imshow("2", image)
    output_image, _ = isOpen(image, face_mesh_results, 'MOUTH', threshold=15, display=False)
    output_image, _ = isOpen(output_image, face_mesh_results, 'LEFT EYE', threshold=5, display=False)
    isOpen(output_image, face_mesh_results, 'RIGHT EYE', threshold=5)