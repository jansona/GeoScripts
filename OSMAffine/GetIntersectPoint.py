# yangzhen
# 2020.11.09


def GetIntersectPoint(img):
    """获取骨架线影像的交点坐标
       img:二值图,0 or 255"""
    import numpy as np
    img = img/255
    rows, cols = img.shape[0:2]
    intersectp = []
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            p1 = img[i, j]
            if (p1 != 1):
                continue
            p2 = img[i-1, j]
            p3 = img[i-1, j+1]
            p4 = img[i, j+1]
            p5 = img[i+1, j+1]
            p6 = img[i+1, j]
            p7 = img[i+1, j-1]
            p8 = img[i, j-1]
            p9 = img[i-1, j-1]
            if ((p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9) != 1):
                ap = 0
                if (p2 == 0 and p3 == 1):
                    ap = ap + 1
                if (p3 == 0 and p4 == 1):
                    ap = ap + 1
                if (p4 == 0 and p5 == 1):
                    ap = ap + 1
                if (p5 == 0 and p6 == 1):
                    ap = ap + 1
                if (p6 == 0 and p7 == 1):
                    ap = ap + 1
                if (p7 == 0 and p8 == 1):
                    ap = ap + 1
                if (p8 == 0 and p9 == 1):
                    ap = ap + 1
                if (p9 == 0 and p2 == 1):
                    ap = ap + 1
                if (ap >= 3):
                    intersectp.append([j, i])
    return np.array(intersectp)


# if __name__ == '__main__':
#     import cv2
#     img = cv2.imread('testlinroad.png', cv2.IMREAD_GRAYSCALE)
#     img[img > 0] = 255
#     intersectp = GetIntersectPoint(img)
#     for i in range(len(intersectp)):
#         cv2.circle(img, (intersectp[i, 0], intersectp[i, 1]), 10, 255)
#     cv2.imwrite('testpoint.png', img)
