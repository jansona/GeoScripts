# yangzhen
# 2020.11.09


import cv2
import numpy as np


def GetImgBound(img):
    """获取二值图白色区域范围"""
    rows, cols = img.shape[0:2]
    # 针对上边界
    i = 0
    while i < rows:
        rowdata = img[i, :]
        num = sum(rowdata == 255)
        if num == cols:
            img = np.delete(img, i, axis=0)
        else:
            break
    # 针对下边界
    rows, cols = img.shape[0:2]
    i = rows - 1
    while i > 0:
        rowdata = img[i, :]
        num = sum(rowdata == 255)
        if num == cols:
            img = np.delete(img, i, axis=0)
            i = i - 1
        else:
            break
    # 针对左边界
    rows, cols = img.shape[0:2]
    i = 0
    while i < cols:
        coldata = img[:, i]
        num = sum(coldata == 255)
        if num == rows:
            img = np.delete(img, i, axis=1)
        else:
            break
    # 针对右边界
    rows, cols = img.shape[0:2]
    i = cols - 1
    while i > 0:
        coldata = img[:, i]
        num = sum(coldata == 255)
        if num == rows:
            img = np.delete(img, i, axis=1)
            i = i - 1
        else:
            break
    nrow, ncol = img.shape[0:2]
    return nrow, ncol


def GetRoadFromMap(map):
    """从地图中获取道路网络
       原理：根据颜色筛选色块
       道路特性：覆盖广，几乎全图分布；道路间连通"""
    # 地图灰度化获取色块
    gmap = cv2.cvtColor(map, cv2.COLOR_BGR2GRAY)
    rows, cols = gmap.shape[0:2]
    road = np.zeros([rows, cols], dtype=np.uint8)
    onlymap = np.unique(gmap)
    num = len(onlymap)
    for i in range(num):
        tmap = np.zeros([rows, cols], dtype=np.uint8)
        tmap[gmap == onlymap[i]] = 255
        img,contours, m2 = cv2.findContours(tmap,  cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        # 根据连通域数目进行一次筛选
        cnum = len(contours)
        if (cnum < 2000):
            # 获取区域大小
            dr, dc = GetImgBound(tmap)
            # 根据连通域范围进行二次筛选
            if (dr > 0.9*rows and dc > 0.9*cols):
                road[gmap == onlymap[i]] = 255
    return road


# if __name__ == '__main__':
#     a = cv2.imread('data/map.tif')
#     gmap = GetRoadFromMap(a)
#     cv2.imwrite('testroad.png', gmap)
