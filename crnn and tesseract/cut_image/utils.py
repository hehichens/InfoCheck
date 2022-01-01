# function

import cv2
from imutils.perspective import four_point_transform
import pytesseract
import os
from PIL import Image
import argparse
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure

def select_info_index(h, count=3, negitive=False):
    index_up = 0
    index_bottom = 0
    max_data = np.max(h)
    flag = False
    for j in range(len(h)):
        if h[j] > max_data * 0.1 and flag == False:
            count -= 1
            index_up = j
            flag = True
        if flag and h[j] < max_data * 0.1:
            flag = False
            if count == 0:
                index_bottom = j
                break
    if negitive:
        for j in range(len(h) - 1, -1, -1):
            if h[j] > max_data * 0.1:
                index_bottom = j
                break

    return index_up - 5, index_bottom + 5


def wraped_org_imgae_save(img, index_list, name_list, path):
    mkdir(path)
    for i, index in enumerate(index_list):
        cv2.imwrite(path + name_list[i] + '.jpg', img[index[0]:index[1], index[2]:index[3], :])


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        print("---  There is this folder!  ---")


def do_v_h(img, is_show=False):
    (h,w) = img.shape
    #垂直投影
    vproject =  img.copy()
    a = [0 for x in range(0,w)]
    #记录每一列的波峰
    for j in range(0,w):#遍历一列
        for i in range(0,h):#遍历一行
            if vproject[i,j]==0:#如果改点为黑点
                a[j]+=1#该列的计数器加1计数
                vproject[i,j]=255#记录完后将其变为白色
    for j in range(0,w):#遍历每一列
        for i in range((h-a[j]),h):#从该列应该变黑的最顶部的点开始向最底部涂黑
            vproject[i,j]=0 #涂黑
    cv2.putText(vproject,"verticality",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1.5,(100,100,100),4)

    #水平投影
    hproject =  img.copy()
    b = [0 for x in range(0,h)]
    for j in range(0,h):
        for i in range(0,w):
            if hproject[j,i] == 0:
                b[j] += 1
                hproject[j,i] = 255
    for j in range(0, h):
        for i in range(0, b[j]):
            hproject[j, i]=0
    cv2.putText(hproject,"horizontal",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1.5,(100,100,100),4)

    if is_show == True:
        plt.figure(figsize=(8,8))
        plt.subplot(2,2,2)
        plt.imshow(img)
        plt.subplot(2,2,4)
        plt.imshow(vproject)
        plt.subplot(2,2,1)
        plt.imshow(hproject)
    return vproject, a, hproject, b
# 绘图展示
def cv2_show(name, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()