# yangzhen
# 2020.11.09
# 原文链接:https://blog.csdn.net/weixin_45675371/article/details/106199985


import numpy as np


def GetRoadLine(img):
    """使用skimage提取骨架线"""
    from skimage import morphology
    img[img > 0] = 1
    lineimg = morphology.skeletonize(img)
    return np.uint8(255*lineimg)


# if __name__ == '__main__':
#     import cv2
#     img = cv2.imread('testroad.png', cv2.IMREAD_GRAYSCALE)
#     thinddd = GetRoadLine(img)
#     cv2.imwrite('testlinroad.png', thinddd)
