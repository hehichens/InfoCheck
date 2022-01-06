"""
functions used to process face image
"""

import face_recognition
import cv2
import numpy as np
import os




def setNames(path):
    """
    set the picture file name as real name
    Params:
        path: a directory containing face images
    Return:
        total_image_name: a list containing names
    """
    total_image_name = []
    for fn in os.listdir(path):
        fn = fn[:(len(fn) - 4)]
        total_image_name.append(fn) 
    return total_image_name


def setFaceEncoding(path):
    """
    create face encoding list
    Params:
        path: a directory containing face images
    Return:
        total_face_encoding: a list containing all the face encoding
    """
    total_face_encoding = []
    for fn in os.listdir(path):  #fn 表示的是文件名q
        total_face_encoding.append(
            face_recognition.face_encodings(
                face_recognition.load_image_file(path + "/" + fn))[0])
        img = face_recognition.load_image_file(path + "/" + fn)
        print(type(img), img.shape)

    return total_face_encoding


def faceRecognition(img, path="../face_images"):
    """
    input an image, then recognize it's name
    Params:
        path: a directory containing face images
    Return:
        name: if there is name in the images directory, then return it's name, whereas return unknown
    """
    ## step1: create name and image list
    total_image_name = setNames(path)
    total_face_encoding = setFaceEncoding(path)

    ## step2, match the image and return it's name
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)
    face_encoding = face_encodings[0]
    for i, v in enumerate(total_face_encoding):
        match = face_recognition.compare_faces(
                [v], face_encoding, tolerance=0.5)
        name = "Unknown"
        if match[0]:
            name = total_image_name[i]

    return name


def getFace(frame, debug=False):
    """
    get a face image from camera
    Params:
        frame: a frame got from camera
    Return: face image
    """
    face_cascade = cv2.CascadeClassifier('../ImageSegmentation/xml/haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    maxi = 0
    maxArea = 0
    for i in range(len(faces)):
        x, y, w, h = faces[i]
        area = w*h
        if area > maxArea:
            maxi = i
            maxArea = area
    
    x, y, w, h = faces[maxi]

    ## bigger image of face
    # flex_x = 0.1
    # flex_y = 0.4
    # x -= int(flex_x*w)
    # y -= int(flex_y*y)
    # w += int(flex_x*w)
    # h += int(flex_y*h)
    faceImg = frame[y:y+h, x:x+w]

    ## debug
    if debug:
        return faceImg, x, y, w, h

    return faceImg
