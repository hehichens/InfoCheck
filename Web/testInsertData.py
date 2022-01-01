
import sqlite3 as sq
import cv2
import sys; sys.path.append("../")
from OCR.baiduOcr import ocrFully

faceImg = cv2.imread("../face_images/ssh.jpg")
text_data = ocrFully()


conn = sq.connect('data.sqlite')
cursor = conn.cursor()
faceImgBlob = sq.Binary(faceImg)
sqText = "insert into user(ID, name, sex, nation, birth, address, cardImg, cardImgHeight, cardImgWidth) values(?, ?, ?, ?, ?, ?, ?, ?, ?);"
cursor.execute(sqText, (text_data[5], text_data[0], text_data[1], text_data[2], text_data[3], text_data[4], faceImgBlob, faceImg.shape[0], faceImg.shape[1]))
conn.commit()
print("insert done!")
conn.close()