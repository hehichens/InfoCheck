"""
https://console.bce.baidu.com/ai/#/ai/ocr/app/detail~appId=3009406
https://learnku.com/articles/48651
"""
import cv2
from aip import AipOcr

""" 你的 APPID AK SK  图2的内容"""
APP_ID = '25439098'
API_KEY = 'AMCujSUGRlcHW9rgEnXzZ9Ov'
SECRET_KEY = 'CpYQ9eRC41Wt7oEDY6IcPiwdILhcictL'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

fname = '../temp_images/card_address_2.jpg'

""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content(fname)

""" 调用通用文字识别, 图片参数为本地图片 """
results = client.general(image)["words_result"]  # 还可以使用身份证驾驶证模板，直接得到字典对应所需字段

print(results[0]['words'])