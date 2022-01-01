"""
this is a web interface
eidt by hichens
"""

from flask import Response
from flask import Flask, request, redirect, url_for
from flask import render_template
import datetime
import cv2
import sys; sys.path.append("../")
import os
import sqlite3 as sq
from FaceRecognition import functions as fc
import OCR.baiduOcr as ocr
import threading
from werkzeug.utils import secure_filename

capFlag = False
lock = threading.Lock()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = datetime.timedelta(seconds=1) # file refresh time
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024 # maximum file  <= 160MB

baseDir = os.path.abspath(os.path.dirname(__file__))
dataBaseDir = os.path.join(baseDir, 'DataBase')

"""global paramters"""
faceImg = None
outputFrame = None
ALLOWED_EXTENSIONS = set(['jpg', 'png'])

@app.route("/index")
@app.route("/")
def index():
    # return the rendered template
    global capFlag 
    capFlag = False
    return render_template("index.html")


@app.route("/main")
def main():
    global capFlag 
    capFlag = True
    if faceImg == None:
        return render_template("main.html")
    else:
        return redirect(url_for('result'))

@app.route("/result")
def result():
    global faceImg, capFlag
    capFlag = False
    name = fc.faceRecognition(faceImg)
    data = []
    Result = []
    return render_template("result.html", data=data, Result=Result)

# @app.route("/PorcessError")
# def ProcessError():
#     return render_template("ProcessError.html")


def detect():
    global capFlag
    cap = cv2.VideoCapture(0)
    global faceImg, outputFrame
    while True:
        if capFlag == False:
            break
        ret, frame = cap.read()
        if ret:
            with lock:
                scale_percent = 700  # percent of original size
                width = scale_percent
                height = scale_percent * frame.shape[0] // frame.shape[1]
                frame = cv2.resize(frame, (width, height))
                """get the face image"""
                outputFrame = frame.copy()
                if faceImg == None:
                    try:
                        faceImg = fc.getFace(frame)
                    except:
                        pass


def generate():

    global outputFrame, lock
    t = threading.Thread(target=detect)
    t.daemon = True
    t.start()
    while True:
        with lock:
            if outputFrame is None:
                continue
            (temp, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not temp:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
            bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            ## save the id card image
            fileName = secure_filename(file.filename)
            dirName = fileName.split(".")[0]
            saveDir = os.path.join(dataBaseDir, dirName)
            os.system("mkdir " + saveDir)
            savePath = os.path.join(saveDir, fileName)
            file.save(savePath)
            cardImg = cv2.imread(savePath)

            ## step2 ocr process get the information of image
            text_data = ocr.ocrFully(savePath)

            ## step3 crop the face image
            faceImg = fc.getFace(cardImg)
            savePath = os.path.join(saveDir, 'face.jpg')
            cv2.imwrite(savePath, faceImg)
            faceImg = cv2.imread(savePath)

            ## step4 save text_data and faceImg to data.sqlite
            save2DataBase(text_data, faceImg)

    return redirect(url_for('index')+"#2")


def save2DataBase(text_data, faceImg):
    ## step1 connet to database
    conn = sq.connect('data.sqlite')
    cursor = conn.cursor()
    try:
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
    except:
        pass
    faceImgBlob = sq.Binary(faceImg)
    sqText = "insert into user(ID, name, sex, nation, birth, address, cardImg, cardImgHeight, cardImgWidth) values(?, ?, ?, ?, ?, ?, ?, ?, ?);"
    cursor.execute(sqText, (text_data[5], text_data[0], text_data[1], text_data[2], text_data[3], text_data[4], faceImgBlob, faceImg.shape[0], faceImg.shape[1]))
    conn.commit()
    print("insert done!")
    conn.close()




@app.route('/videoprocess', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        return redirect(url_for('main'))
    else:
        return redirect(url_for('index')+"#2")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# @app.route('/cameraprocess', methods=['GET', 'POST'])
# def camerapage():
#     if request.method == 'POST':
#         return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False,
            threaded=True, use_reloader=False)