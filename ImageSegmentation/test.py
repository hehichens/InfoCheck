"""
test the result of images segmentation
edit by Hichens Dec/30/2021
"""

import cv2
from split import imgSplit


if __name__ == "__main__":
    img_path = "../images/w1.jpg"
    img = cv2.imread(img_path)

    ## detect
    imgSplit(img)