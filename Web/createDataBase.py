import sqlite3 as sq
import os
import cv2

import sys; sys.path.append("..")
import FaceRecognition.functions as fc
from OCR.baiduOcr import ocrFully


## connetc sqlite
conn = sq.connect('data.sqlite')
print("connnect done!")
cursor = conn.cursor()

# create table
"""
ID: the id card number
name: name in the id card
sex: 男 or 女
nation: 民族
birth: 生日(eg: 1984年10月1日)
cardImg: the image of id card with byte form
cardImgHeight: the height of image(in order to reshape)
cardImgWidth: the width of image

the example of insert data:
==> sqText = "insert into user(ID, name, sex, nation, birth, address, cardImg, cardImgHeight, cardImgWidth) values(?, ?, ?, ?, ?, ?, ?, ?, ?);"
==> cursor.execute(sqText, ('111111111111111111', '张三', '男', '汉族', '1984年10月1日', '重庆市xxx', img_blob, img.shape[0], img.shape[1]))
"""
try:
    cursor.execute('''create table user
    (
        ID varchar(20) primary key,
        name varchar(20),
        sex varchar(4),
        nation varchar(10),
        birth varchar(20),
        address varchar(40),
        cardImg blob,
        cardImgHeight int, 
        cardImgWidth int
    );''')
    print("create table done!")
except:
    pass

sqText = "insert into user(ID, name, sex, nation, birth, address, cardImg, cardImgHeight, cardImgWidth) values(?, ?, ?, ?, ?, ?, ?, ?, ?);"
for filename in os.listdir("../images"):
    path = os.path.join("../images", filename)
    # print(path)
    text_data = ocrFully(path)
    img = cv2.imread(path)
    faceImg = fc.getFace(img)
    faceImgBlob = sq.Binary(faceImg)
    cursor.execute(sqText, (text_data[5], text_data[0], text_data[1], text_data[2], text_data[3], text_data[4], faceImgBlob, faceImg.shape[0], faceImg.shape[1]))
conn.commit()
print("insert done!")

conn.close()