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

    """debug"""
    # contour = pc.addContours(img, regions)
    # debug_show(contour)
    

    ## step4: split region
    pc.splitFace(img)
    for rect in regions:
        cropImg = pc.projMap(img, rect)
        # debug_show(cropImg)
        pc.splitCardNum(cropImg)

        CropImg, point, width, hight = pc.cropImgByRect(img, rect)
        box = pc.findChineseCharArea(point, width, hight)
        chiCharArea, point, width, hight = pc.cropImgByBox(img, box)
        # pc.debug_show(chiCharArea)

        kernelx = kernely = int(math.ceil((hight / 100.0)))
        kernel_size = (kernelx, kernely)
        pc.splitChineseChar(chiCharArea, kernel_size)

    print("split done !")
    

    ## 

    ## debug
    # debug_show(th)