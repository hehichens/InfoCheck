"""

"""

import cv2
import numpy as np
import face_recognition
import sqlite3 as sq

def faceMatch(faceImg):
    """
    Params:
        faceImg: a face image
    return
        name: the name of the image
    """
    ##step 1 load all the name from data.sqlite
    conn = sq.connect('data.sqlite')
    cursor = conn.cursor()
    sqText = "select * from user;"
    data = cursor.execute(sqText)
    

    ## step2 create name and image list
    total_face_encoding = []
    total_image_name = []
    for raw in data:
        
        total_image_name.append(raw[1])
        img = np.frombuffer(raw[6], dtype=np.uint8)
        height, width = raw[7], raw[8]
        img = img.reshape(height, width, 3)

        ##debug
        cv2.imshow("img", img)
        cv2.waitKey()

        total_face_encoding.append(
            face_recognition.face_encodings(img)[0]
        )

    ## step3 match the image and return it's name
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)
    face_encoding = face_encodings[0]
    for i, v in enumerate(total_face_encoding):
        match = face_recognition.compare_faces(
                [v], face_encoding, tolerance=0.9)
        if match[0]:
            name = total_image_name[i]
        else:
            name = "未知"

    ##debug
    print(len(total_face_encoding))
    print(total_image_name)

    conn.close()
    return name


if __name__ == "__main__":
    faceImg = cv2.imread("./DataBase/hc/face.jpg")
    name = faceMatch(faceImg)
    # cv2.imshow("faceImg", faceImg)
    # cv2.waitKey()
    print(name)