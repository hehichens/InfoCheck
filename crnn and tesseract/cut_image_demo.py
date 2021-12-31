import cv2
from imutils.perspective import four_point_transform
import pytesseract
import os
import numpy as np
from cut_image.utils import select_info_index, cv2_show, wraped_org_imgae_save, do_v_h

img_name = 'w31'
img = cv2.imread("./images/" + img_name + '.jpg')
img = cv2.resize(img, None,fx=0.2,fy=0.2)
h,w = img.shape[:2]
# mask = np.zeros((h + 2, w + 2), np.uint8)
# cv2.floodFill(img, mask, (0, 0), (0,0,0), (2,2,2), (3,3,3), 8)
blur = cv2.GaussianBlur(img, (5, 5), 0)
gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
edged = cv2.Canny(gray, 60, 200)
# cv2_show('uhudsf', edged)

# 轮廓检测
cnts, hierancy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# # 找出图像中的轮廓
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]  # 将轮廓按照面积的大小进行排序，并且选出前5个中最大的轮廓，当多个小票时
for c in cnts:
    peri = cv2.arcLength(c, True)  # 周长，闭合
    approx = cv2.approxPolyDP(c, 0.02* peri, True)  # 检测出来的轮廓可能是离散的点，故因在此做近似计算，使其形成一个矩形
    if len(approx)== 4:  # 如果检测出来的是矩形，则break本段if
        screenCnt = approx
# cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 2)  # 绘制轮廓，-1表示全部绘制
# cv2_show('contour', img)

wraped_img = four_point_transform(img, screenCnt.reshape(4, 2))
wraped = cv2.GaussianBlur(wraped_img, (17, 17), 0)
wraped = cv2.cvtColor(wraped, cv2.COLOR_BGR2GRAY)
ref = cv2.adaptiveThreshold(wraped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2, 2))
process_img = cv2.dilate(ref, kernel)
# cv2_show('sdjfisdf', wraped_img)

# cut_id
vproject, a, hproject, b = do_v_h(process_img, False)
id_b = b[int(len(b)*0.8):]
max_id = np.max(id_b)
max_id_index = np.argmax(id_b)
id_bottom = max_id_index - 1
id_up = max_id_index + 1
while True:
    if id_bottom <= 0 or id_b[id_bottom] <= 0.1 * max_id:
        break
    id_bottom -= 1
while True:
    if id_up >= len(b) or id_b[id_up] <= 0.1 * max_id:
        break
    id_up += 1
id_img = wraped_img[int(len(b)*0.8) + id_bottom - 10: int(len(b) * 0.8) + id_up + 10,:,:]


id_blur = cv2.GaussianBlur(id_img, (27, 27), 0)
id_gray = cv2.cvtColor(id_blur, cv2.COLOR_BGR2GRAY)
id_ref = cv2.adaptiveThreshold(id_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 2)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(23, 23))
id_ref = cv2.erode(id_ref, kernel)
vproject, ah, hproject, bh = do_v_h(id_ref, False)
index_up, index_bottom =  select_info_index(ah, 1, negitive=True)
res_id_img = id_img[:, index_up:index_bottom,:]


new_wraped_img = wraped_img[:int(len(b)*0.8)+id_bottom,:,:]
blur = cv2.GaussianBlur(new_wraped_img, (7, 7), 0)
gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
ret, new_pro_img = cv2.threshold(gray,60,255,cv2.THRESH_BINARY)
vproject, a, hproject, b = do_v_h(new_pro_img, False)

max_head = np.max(a)
max_head_index = np.argmax(a)
head_bottom = max_head_index - 1
while True:
    if head_bottom <= 0 or a[head_bottom] <= 0.1 * max_head:
        break
    head_bottom -= 1

no_head_img = process_img[:int(len(b) * 0.8) + id_bottom, : head_bottom - 10]
no_head_org_img = wraped_img[:int(len(b) * 0.8) + id_bottom, : head_bottom - 10]
no_head_img = cv2.dilate(no_head_img, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
no_head_img = cv2.erode(no_head_img, cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11)))
# cv2_show('no_head_img', no_head_org_img)
vproject, ah, hproject, bh = do_v_h(no_head_img, False)
max_data = np.max(b)
index_list = []
index_up = 0
index_bottom = np.inf
flag = False
for i in range(len(bh)):
    if bh[i] > max_data * 0.2 and flag == False:
        index_up = i
        flag = True
    if flag and bh[i] < max_data * 0.2:
        index_bottom = i
        flag = False
        index_list.append([index_up - 5, index_bottom + 5])



index_all_list = []
for i, index in  enumerate(index_list):
    pic = no_head_img[index[0]: index[1], :]
    vproject, ah, hproject, bh = do_v_h(pic, False)
    if i == 0:
        index_up, index_bottom =  select_info_index(ah)
    if i == 1:
        index_up, index_bottom =  select_info_index(ah)
        index_all_list.append([index[0], index[1], index_up, index_bottom])
        index_up, index_bottom =  select_info_index(ah, 6)
    if i == 2:
        index_up, index_bottom =  select_info_index(ah, negitive=True)
    if i == 3:
        index_up, index_bottom =  select_info_index(ah)
    if i == 4:
        index_up, index_bottom =  select_info_index(ah, 1, negitive=True)
    index_all_list.append([index[0], index[1], index_up, index_bottom])


name_list = ['name', 'sex', 'nation', 'birth', 'area1', 'area2']
path = './crnn  and tesseract/image/' + img_name + '/'
wraped_org_imgae_save(no_head_org_img, index_all_list, name_list, path)
cv2.imwrite(path + 'id.jpg',res_id_img)

files = os.listdir(path)  # 得到文件夹下的所有文件名称
result = {'area': ''}
for file in files:
    if not os.path.isdir(file):
        img = cv2.imread(path + file)
        name = file.replace('.jpg', '')
        name = name.replace('.png', '')

        if name == 'birth':
            blur = cv2.GaussianBlur(img, (11, 11), 0)
            gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
            ref = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            img = cv2.dilate(ref, kernel)
        #         cv2_show('sdhaud', ref)

        text = pytesseract.image_to_string(img, lang='chi_sim')
        text = text.replace('\n', '')
        text = text.replace('\x0c', '')
        text = text.replace(' ', '')
        print(text)
        if name == 'area1' or name == 'area2':
            result['area'] += text
        else:
            result[name] = text
print(result)