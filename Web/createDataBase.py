import sqlite3 as sq


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
conn.close()