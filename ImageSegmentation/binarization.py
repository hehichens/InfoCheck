"""
include kinds of banarization algorithm
edit by Hichens Dec/30/2021
"""

import cv2
import math

def getMinimumThreshold(img):
    """
    谷底最小值的阈值
    """
    Y = Iter = 0
    HistGramC = []
    HistGramCC = []

    #获取直方数组
    hist = getHisGram(img)

    for Y in range(256):
        HistGramC.append(hist[Y])
        HistGramCC.append(hist[Y])

    #通过三点求均值来平滑直方图
    while( isDimodal(HistGramCC) == False):
        HistGramCC[0] = (HistGramC[0] + HistGramC[0] + HistGramC[1]) / 3.0 #第一点
        for Y in range(1, 255):
            HistGramCC[Y] = (HistGramC[Y - 1] + HistGramC[Y] + HistGramC[Y + 1]) / 3 #中间的点

        HistGramCC[255] = (HistGramC[254] + HistGramC[255] + HistGramC[255]) / 3 #最后一点
        HistGramC = HistGramCC
        Iter += 1
        if (Iter >= 1000):
            return -1

    #阈值极为两峰之间的最小值
    Peakfound = False
    for Y in range(1, 255):
        if (HistGramCC[Y - 1] < HistGramCC[Y] and HistGramCC[Y + 1] < HistGramCC[Y]):
            Peakfound = True
        if (Peakfound == True and HistGramCC[Y - 1] >= HistGramCC[Y] and HistGramCC[Y + 1] >= HistGramCC[Y]):
            return Y - 1
    return -1


def get1DMaxEntropyThreshold(img):
    """
    一维最大熵
    """
    X = Y = Amount = 0
    HistGramD = {}
    MinValue = 0
    MaxValue = 255
    Threshold = 0

    HistGram = getHisGram(img)

    for i in range(256):
        if HistGram[MinValue] == 0:
            MinValue += 1
        else:
            break

    while MaxValue > MinValue and HistGram[MinValue] == 0:
        MaxValue -= 1

    if (MaxValue == MinValue):
        return MaxValue     #图像中只有一个颜色
    if (MinValue + 1 == MaxValue):
        return MinValue     #图像中只有二个颜色

    for Y in range(MinValue, MaxValue + 1):
        Amount += HistGram[Y]  #像素总数

    for Y in range(MinValue, MaxValue + 1):
        HistGramD[Y] = HistGram[Y] / Amount +1e-17

    MaxEntropy = 0.0
    for Y in range(MinValue + 1, MaxValue):
        SumIntegral = 0
        for X in range(MinValue, Y + 1):
            SumIntegral += HistGramD[X]

        EntropyBack = 0
        for X in range(MinValue, Y + 1):
            EntropyBack += (- HistGramD[X] / SumIntegral * math.log(HistGramD[X] / SumIntegral))

        EntropyFore = 0
        for X in range(Y + 1, MaxValue + 1):
            SumI = 1 - SumIntegral
            if SumI < 0:
                SumI = abs(SumI)
            elif SumI == 0:
                continue

            EntropyFore += (- HistGramD[X] / (1 - SumIntegral) * math.log(HistGramD[X] / SumI))

        if MaxEntropy < (EntropyBack + EntropyFore):
            Threshold = Y
            MaxEntropy = EntropyBack + EntropyFore

    if Threshold > 5:
        return Threshold - 5 #存在误差
    return Threshold



"""other functions"""
def getHisGram(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    return hist


def isDimodal(HistGram):
    Count = 0
    for Y in range(1, 255):
        if HistGram[Y - 1] < HistGram[Y] and HistGram[Y + 1] < HistGram[Y]:
            Count += 1
            if(Count > 2):
                return False

    if Count == 2:
        return True
    else:
        return False
