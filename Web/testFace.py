"""
test face match
"""
import face_recognition
import numpy as np
import sqlite3 as sq
import cv2
import time

import sys; sys.path.append("../")
from FaceRecognition import functions as fc


total_face_encoding = []
total_image_name = []


def faceMatch(frame):
    name = 'Unknown'
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    top, right, bottom, left = face_locations[0]
    face_encoding = face_encodings[0]

    # 看看面部是否与已知人脸相匹配
    for i, v in enumerate(total_face_encoding):
        match = face_recognition.compare_faces(
            [v], face_encoding, tolerance=0.4)
        name = "Unknown"
        if match[0]:
            name = total_image_name[i]
            # print(name)
            break

    return name


def connetDB():
    """
    connetc to sqlite
    """
    conn = sq.connect('data.sqlite')
    cursor = conn.cursor()
    sqText = "select * from user;"
    data = cursor.execute(sqText)
    for raw in data:
        total_image_name.append(raw[1])
        img = np.frombuffer(raw[6], dtype=np.uint8)
        height, width = raw[7], raw[8]
        img = img.reshape(height, width, 3)
        total_face_encoding.append(
            face_recognition.face_encodings(img)[0])


if __name__ == "__main__":
    connetDB()
    cap = cv2.VideoCapture(0)
    name = 'Unknown'
    start = time.time()
    while True:
        ret, frame = cap.read()
        scale_percent = 700  # percent of original size
        width = scale_percent
        height = scale_percent * frame.shape[0] // frame.shape[1]
        frame = cv2.resize(frame, (width, height))
        _, x, y, w, h = fc.getFace(frame, debug=True)
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.imshow("main window", frame)
        try:
            name = faceMatch(frame)
        except:
            pass
        print(name)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if time.time() - start > 8:
            break


cv2.destroyAllWindows()