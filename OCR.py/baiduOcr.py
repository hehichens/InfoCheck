"""
https://console.bce.baidu.com/ai/#/ai/ocr/app/detail~appId=3009406
https://learnku.com/articles/48651
"""
from aip import AipOcr



def ocr(img_path='../temp_images/card_address_2.jpg'):
    """
    Trasform the part of image characters to text with Bai Du OCR
    Params:
        img_path: the path of your image
    Return:
        a string
    """
    APP_ID = '25439098'
    API_KEY = 'AMCujSUGRlcHW9rgEnXzZ9Ov'
    SECRET_KEY = 'CpYQ9eRC41Wt7oEDY6IcPiwdILhcictL'

    with open(img_path, 'rb') as fp:
        img = fp.read()
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    try:
        results = client.general(img)
        text_data = results["words_result"]["words_result"]
    except:
        text_data = ''
    return text_data


def ocrFully(img_path='../images/w1.jpg'):
    """
    Trasform the whole image characters to text with Bai Du OCR
    Params:
        img_path: the path of your image
    Return:
        a dict contrained the all the text
    """
    APP_ID = '25439098'
    API_KEY = 'AMCujSUGRlcHW9rgEnXzZ9Ov'
    SECRET_KEY = 'CpYQ9eRC41Wt7oEDY6IcPiwdILhcictL'

    with open(img_path, 'rb') as fp:
        img = fp.read()
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    text_data = []
    try:
        results = client.general(img)
        return_data = results["words_result"]
    except:
        pass
        
    for i, data in enumerate(return_data):
        if i == 0 and data[0] == '姓' and data[1] == '名':
            text_data.append(data[2:])
        elif i == 1 and data[0] == '性' and data[1] == '别':
            text_data.append(data[2])
        elif i == 1 and data[3] == '民' and data[4] == '民族':
            text_data.append(data[5])
        elif i == 2 and data[0] == '出' and data[1] == '生':
            text_data.append(data[2:])
        elif i == 3 and data[0] == '住' and data[1] == '址':
            text_data.append(data[2:])
        elif i == 3 and data[0] != '公' and data[1] != '民':
            text_data.append(data[:])
        
        

    return text_data



if __name__ == "__main__":
    text = ocr("../images/w1.jpg")
    print(text)
