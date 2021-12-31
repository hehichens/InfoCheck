"""
test face recognition
"""

import functions as fc
import cv2


if __name__ == "__main__":
    img = cv2.imread('../temp_images/card_face.jpg')
    name = fc.faceRecognition(img)
    print(name)