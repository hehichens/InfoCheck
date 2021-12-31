"""
all the function about process images
edit by Hichens Dec/30/2021
"""

import cv2
import math
import binarization as bz
import numpy as np


"""show image"""
def debug_show(img):
    """
    show image
    Params:
        img: any image
    Return:
        None
    """
    cv2.imshow("debug window", img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def addContours(img, regions):
    """
    Params:
        img: an image
        regions: rectangle objects which found with findContours
    Return:
        img: an image after add contour
    """
    for rect in regions:
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(img, [box], 0, (0, 255, 0), 3)

    return img



"""image process"""
def preprocess(img):
    """
    Params:
        img: gray image
    Return:
        dilation: preprocess image
    """
    ## step1:bulr
    kernel_size = (5, 5) ## ==>flag<==
    # blur = cv2.GaussianBlur(img, kernel_size, 0)
    blur = img

    ## step2: binarize
    # ret,binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    threshold = bz.get1DMaxEntropyThreshold(blur)
    ret, binary = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY)


    ## step3: dilate and erode
    ### Calucale the kernel
    kernel_size = calKernelSize(blur)
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)

    ### remove the little noise
    dilation = cv2.dilate(binary, kernel1, iterations=1)
    binary = cv2.erode(dilation, kernel1, iterations=1)

    ### link together
    erosion = cv2.erode(binary, kernel2, iterations=1)
    dilation = cv2.dilate(erosion, kernel1, iterations=1)

    ## debug
    # debug_show(binary)
    # debug_show(dilation)

    return dilation



def findTextRegion(img):
    """
    Params:
        img: an image after preprocess
    Return:
        regions: rectangle objects which found with findContours
    """
    regions = []
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:

        ## step1: remove the area which is too small
        area = cv2.contourArea(cnt)
        if area < 1000:
            continue

        ## step2: find the rectangle with angle
        rect = cv2.minAreaRect(cnt)

        ## step3 remove the rectanlge which is to0 'squre'
        width, height = rect[1][0], rect[1][1]
        if width/5 < height < width*5:
            continue

        regions.append(rect)
    return regions


def calKernelSize(img):
    """
    
    """
    sp = img.shape
    width = sp[1]  # width(colums) of image
    kenaly = math.ceil((width / 400.0) * 12)
    kenalx = math.ceil((kenaly / 5.0) * 4)
    kernel_size = (int(kenalx), int(kenaly))

    return kernel_size


def projMap(img, rect):
    """
    Params:
        img: image
        rect: https://blog.csdn.net/lanyuelvyun/article/details/76614872
    Return:
        cropImg: image after projection map
    """
    angle = rect[2]
    a, b = rect[1]
    if a > b:
        width = a
        hight = b
        pts2 = np.float32([[0, hight], [0, 0], [width, 0], [width, hight]])
    else:
        width = b
        hight = a
        angle = 90 + angle
        pts2 = np.float32([[width, hight], [0, hight], [0, 0], [width, 0]])

    box = cv2.boxPoints(rect)
    pts1 = np.float32(box)
    M = cv2.getPerspectiveTransform(pts1, pts2)
    cropImg = cv2.warpPerspective(img, M, (int(width), int(hight)))
    
    return cropImg


def splitCardNum(img, path='../temp_images/card_num.jpg'):
    """
    save the card number images
    """
    cv2.imwrite(path, img)


def cropImgByRect(img, rect):
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    return cropImgByBox(img, box)
    


def cropImgByBox(img, box):
    """
    通过顶点矩阵，裁剪图片
    :param imgSrc:
    :param box:
    :return:
    """

    Xs = [i[0] for i in box]
    Ys = [i[1] for i in box]
    x1 = min(Xs)
    x2 = max(Xs)
    y1 = min(Ys)
    y2 = max(Ys)
    hight = y2 - y1
    width = x2 - x1

    # enlarge the img
    # y_flex = int(0*hight)
    # x_flex = int(0*width)

    # y_start = max(y1-y_flex, 0)
    # x_start = max(x1-x_flex, 0)

    # 裁剪
    cropImg = img[y1:y1 + hight, x1:x1 + width]
    # cropImg = imgSrc[y_start:y1 + hight+y_flex, x_start:x1 + width+x_flex]

    return cropImg, (x1, y1), width, hight



def findChineseCharArea(cardNumPoint1, width, hight):
    """
    根据身份证号码的位置推断姓名、性别、名族、出生年月、住址的位置
    :param cardNumPoint1: tuple 身份证号码所处的矩形的左上角坐标
    :param width: int 身份证号码所处的矩形的宽
    :param hight: int 身份证号码所处的矩形的高
    :return:
    """
    #new_x = int(cardNumPoint1[0] - (width / 18) * 6)
    new_x = cardNumPoint1[0] - (width / 18) * 5.5
    new_width = int(width/5 * 4)

    box = []
    #new_y = cardNumPoint1[1] - hight * 6.5
    card_hight = hight / (0.9044 - 0.7976)   #身份证高度
    card_y_start = cardNumPoint1[1] - card_hight * 0.7976 #粗略算出图像中身份证上边界的y坐标

    #为了保证不丢失文字区域，姓名的相对位置保留，以身份证上边界作为起始切割点
    #new_y = card_y_start# + card_hight * 0.0967

    #容错因子，防止矩形存在倾斜导致区域重叠
    factor = 20

    new_y = card_y_start if card_y_start > factor else factor

    new_hight = card_hight * (0.7616 - 0.0967) + card_hight * 0.0967

    #文字下边界坐标
    new_y_low = (new_y + new_hight) if (new_y + new_hight) <= cardNumPoint1[1] - factor else cardNumPoint1[1] - factor

    box.append([new_x, new_y])
    box.append([new_x + new_width, new_y])
    box.append([new_x + new_width, new_y_low])
    box.append([new_x, new_y_low])

    box = np.int0(box)
    return box


def splitChineseChar(img, kernel_size):
    """
    
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshold = bz.get1DMaxEntropyThreshold(img)
    ret, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    boundaryCoors = horizontalProjection(binary)
    # print(boundaryCoors)
    for i, boundaryCoor in enumerate(boundaryCoors):
        coors = chineseCharHandle(binary, boundaryCoor)
        up, down = boundaryCoor
        box = np.int0([[coors[0][0], up], [coors[-1][1], up], [coors[-1][1], down], [coors[0][0], down]])
        cropImg, _, _, _  = cropImgByBox(img, box)
        # debug_show(cropImg)
        if i == 0:
            cv2.imwrite("../temp_images/card_name.jpg", cropImg)
        elif i == 1:
            cv2.imwrite("../temp_images/card_sex_nation.jpg", cropImg)
        elif i == 2:
            cv2.imwrite("../temp_images/card_birthday.jpg", cropImg)
        else:
            cv2.imwrite("../temp_images/card_address_%d.jpg"%(i-2), cropImg)





def horizontalProjection(BinaryImg):
    """
    水平投影边界坐标
    :return:
    """
    #水平行边界坐标
    boundaryCoors = []
    (x, y) = BinaryImg.shape
    a = [0 for z in range(0, x)]

    for i in range(0, x):
        for j in range(0, y):
            if BinaryImg[i, j] == 0:
                a[i] = a[i] + 1
                #BinaryImg[i, j] = 255  # to be white

    #连续区域标识
    continuouStartFlag = False
    up = down = 0
    tempUp = 0  #行高不足总高1/20,临时保存，考虑与下一个行合并。主要解决汉字中上下结构的单子行像素点不连续的问题

    for i in range(0, x):
        # for j in range(0, a[i]):
        #     BinaryImg[i, j] = 0

        if a[i] > 1 :
            if not continuouStartFlag:
                continuouStartFlag = True
                up = i
        else:
            if continuouStartFlag:
                continuouStartFlag = False
                down = i - 1
                if down - up >= x / 20 and down -up <= x/10:
                    #行高小于总高1/20的抛弃
                    boundaryCoors.append([up, down])
                else:
                    if tempUp > 0:
                        if down - tempUp >= x / 20 and down - tempUp <= x/10:
                            # 行高小于总高1/20的抛弃
                            boundaryCoors.append([tempUp, down])
                            tempUp = 0
                    else:
                        tempUp = up

    #print boundaryCoors
    #showImg(BinaryImg, 'BinaryImg')
    if len(boundaryCoors) < 4:
        return False

    return boundaryCoors


def chineseCharHandle(BinaryImg, horiBoundaryCoor):
    fator = 0.9

    vertiBoundaryCoors, maxWidth = CardCharCommonDeal(BinaryImg, horiBoundaryCoor)
    newVertiBoundaryCoors = []  # 字符合并后的垂直系列坐标

    charNum = len(vertiBoundaryCoors)

    i = 0
    while i < charNum:
        if i + 1 >= charNum:
            newVertiBoundaryCoors.append(vertiBoundaryCoors[i])
            break

        curCharWidth = vertiBoundaryCoors[i][1] - vertiBoundaryCoors[i][0]
        if curCharWidth < maxWidth * fator:
            if vertiBoundaryCoors[i + 1][1] - vertiBoundaryCoors[i][0] <= maxWidth*(2 - fator):
                newVertiBoundaryCoors.append([vertiBoundaryCoors[i][0], vertiBoundaryCoors[i + 1][1]])
                i += 1
            elif curCharWidth > maxWidth / 4:
                newVertiBoundaryCoors.append(vertiBoundaryCoors[i])
        else:
            newVertiBoundaryCoors.append(vertiBoundaryCoors[i])

        i += 1
    return newVertiBoundaryCoors


def CardCharCommonDeal(BinaryImg, horiBoundaryCoor):
    """
    文字通用切割处理
    :param BinaryImg:
    :param horiBoundaryCoor:
    :return:
    """
    # 列边界坐标
    vertiBoundaryCoors = []

    up, down = horiBoundaryCoor
    lineHight = down - up

    (x, y) = BinaryImg.shape
    a = [0 for z in range(0, y)]

    for j in range(0, y):
        for i in range(up, down):
            if BinaryImg[i, j] == 0:
                a[j] = a[j] + 1
                #BinaryImg[i, j] = 255  # to be white

    # 连续区域标识
    continuouStartFlag = False
    left = right = 0

    pixelNum = 0  # 统计每个列的像素数量
    maxWidth = 0  #最宽的字符长度
    for i in range(0, y):
        # for i in range((down - a[j]), down):
        #     BinaryImg[i, j] = 0
        pixelNum += a[i]  # 统计像素
        if a[i] > 0:
            if not continuouStartFlag:
                continuouStartFlag = True
                left = i
        else:
            if continuouStartFlag:
                continuouStartFlag = False
                right = i
                if right - left > 0:
                    if pixelNum > lineHight * (right - left) / 10:
                        curW = right - left
                        maxWidth = curW if curW > maxWidth else maxWidth
                        vertiBoundaryCoors.append([left, right])
                    pixelNum = 0  # 遇到边界，归零

    #showImg(BinaryImg, 'BinaryImgBinaryImg')
    return vertiBoundaryCoors, maxWidth


def splitFace(img):
    face_cascade = cv2.CascadeClassifier('./xml/haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
    # cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    # debug_show(img)
    cropImg = img[y:y+h, x:x+w]
    # debug_show(cropImg)
    cv2.imwrite("../temp_images/card_face.jpg", cropImg)



if __name__ == "__main__":
    pass