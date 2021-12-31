import numpy as np
import time
import cv2
import torch
from torch.autograd import Variable
import lib.utils.utils as utils
import lib.models.crnn as crnn
import lib.config.alphabets as alphabets
import yaml
from easydict import EasyDict as edict
import argparse
import os
import pytesseract

def parse_arg():
    parser = argparse.ArgumentParser(description="demo")

    parser.add_argument('--cfg', help='experiment configuration filename', type=str, default='lib/config/360CC_config.yaml')
    # parser.add_argument('--image_path', type=str, default='images/test.png', help='the path to your image')
    parser.add_argument('--checkpoint', type=str, default='output/checkpoints/mixed_second_finetune_acc_97P7.pth',
                        help='the path to your checkpoints')

    args = parser.parse_args()

    with open(args.cfg, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        config = edict(config)

    config.DATASET.ALPHABETS = alphabets.alphabet
    config.MODEL.NUM_CLASSES = len(config.DATASET.ALPHABETS)

    return config, args

def recognition(config, img, model, converter, device, is_print=False):

    # github issues: https://github.com/Sierkinhane/CRNN_Chinese_Characters_Rec/issues/211
    h, w = img.shape
    # fisrt step: resize the height and width of image to (32, x)
    img = cv2.resize(img, (0, 0), fx=config.MODEL.IMAGE_SIZE.H / h, fy=config.MODEL.IMAGE_SIZE.H / h, interpolation=cv2.INTER_CUBIC)

    # second step: keep the ratio of image's text same with training
    h, w = img.shape
    w_cur = int(img.shape[1] / (config.MODEL.IMAGE_SIZE.OW / config.MODEL.IMAGE_SIZE.W))
    img = cv2.resize(img, (0, 0), fx=w_cur / w, fy=1.0, interpolation=cv2.INTER_CUBIC)
    img = np.reshape(img, (config.MODEL.IMAGE_SIZE.H, w_cur, 1))

    # normalize
    img = img.astype(np.float32)
    img = (img / 255. - config.DATASET.MEAN) / config.DATASET.STD
    img = img.transpose([2, 0, 1])
    img = torch.from_numpy(img)

    img = img.to(device)
    img = img.view(1, *img.size())
    model.eval()
    preds = model(img)

    _, preds = preds.max(2)
    preds = preds.transpose(1, 0).contiguous().view(-1)

    preds_size = Variable(torch.IntTensor([preds.size(0)]))
    sim_pred = converter.decode(preds.data, preds_size.data, raw=False)
    if is_print:
        print(preds.shape)
        print('results: {0}'.format(sim_pred))

    return sim_pred


def traditional_identification(img, name):
    if name == 'birth':
        blur = cv2.GaussianBlur(img, (11, 11), 0)
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        ref = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        img = cv2.dilate(ref, kernel)
    # if name  == 'id':
    #     blur = cv2.GaussianBlur(img, (11, 11), 0)
    #     gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    #     ref = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2)
    #     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 2))
    #     img = cv2.dilate(ref, kernel)

    text = pytesseract.image_to_string(img, lang='chi_sim')
    text = text.replace('\n', '')
    text = text.replace('\x0c', '')
    text = text.replace(' ', '')
    return text

def deeplr_identification(img, config, model, device, is_print_time=False):
    started = time.time()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    converter = utils.strLabelConverter(config.DATASET.ALPHABETS)

    pre = recognition(config, img, model, converter, device)
    finished = time.time()
    if is_print_time:
        print('elapsed time: {0}'.format(finished - started))

    return pre

def show_result(path='./image/w31'):
    config, args = parse_arg()
    device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
    # device = torch.device('cpu')

    model = crnn.get_crnn(config).to(device)
    # print('loading pretrained model from {0}'.format(args.checkpoint))
    checkpoint = torch.load(args.checkpoint, map_location=torch.device('cpu'))
    if 'state_dict' in checkpoint.keys():
        model.load_state_dict(checkpoint['state_dict'])
    else:
        model.load_state_dict(checkpoint)

    path =  path + '/'
    files = os.listdir(path)  # 得到文件夹下的所有文件名称
    result = {'address': ''}

    started = time.time()
    for file in files:
        if not os.path.isdir(file):
            img = cv2.imread(path + file)
            name = file.replace('.jpg', '')
            name = name.replace('.png', '')
            name = name.replace('_', '')
            name = name.replace('card', '')

            if name in ['num', 'id', 'birth', 'name']:
                pre = traditional_identification(img, name)
            else:
                pre = deeplr_identification(img, config, model, device)


            if name == 'address1' or name == 'address2' or name == 'area1' or name == 'area2':
                result['address'] += pre
            else:
                result[name] = pre
    finished = time.time()
    # print('elapsed time: {0}'.format(finished - started))
    # print(result)

    return result




