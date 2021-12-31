"""
split the images
edit by Hichens Dec/30/2021
"""


import cv2
import sys
import numpy as np
import math
import process as pc

def imgSplit(img):
    """
    Input the image of ID card, spliting the image to face, id number, sex, nation, name, birthday and address, \
        then saving these images to ../temp_images/*
    Params:
        img: an img opened by opencv
    Return:
        No return
    """

    ## step1: bgr to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ## step2: preprocess
    dilation = pc.preprocess(gray) ##==>OK!<==

    ## step3: find text region
    regions = pc.findTextRegion(dilation)

    ## step4: split region
    pc.splitFace(img) # face
    for rect in regions:
        cropImg = pc.projMap(img, rect)
        pc.splitCardNum(cropImg) # id card number

        CropImg, point, width, hight = pc.cropImgByRect(img, rect)
        box = pc.findChineseCharArea(point, width, hight)
        chiCharArea, point, width, hight = pc.cropImgByBox(img, box)
        # pc.debug_show(chiCharArea)

        kernelx = kernely = int(math.ceil((hight / 100.0)))
        kernel_size = (kernelx, kernely)
        pc.splitChineseChar(chiCharArea, kernel_size) # other area

    print("split done !")
    