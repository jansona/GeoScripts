# yangzhen
# 2020.10.22


import json
import os
import cv2
import numpy as np
from shutil import copyfile,rmtree
import argparse

class inputpath():
    def __init__(self,path):
        #self.pathlist=[]
        if not path.find('\\') == -1:
            self.pathlist=path.split('\\')
        elif not path.find('/') == -1:
            self.pathlist = path.split('/')
        print (self.pathlist)
        self.datasource = self.pathlist[-3]
        self.datatype=self.pathlist[-4]
        self.mainpath='/'.join(self.pathlist[0:-4])
        self.zoompath='/'.join(self.pathlist[-3:])
        self.zoompath1='/'.join(self.pathlist[-2:])

        print (self.mainpath,self.zoompath)

def GetImageTranslation(img1, img2, patchheight=2000, patchwidth=2000):
    """采用平移变换对影像进行配准"""
    mimg1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    mimg2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    mimg1 = np.float32(mimg1)
    mimg2 = np.float32(mimg2)
    dxy = cv2.phaseCorrelate(mimg2, mimg1)
    M = np.float32([[1, 0, dxy[0][0]], [0, 1, dxy[0][1]]])
    nimg2 = cv2.warpAffine(img2, M, (img1.shape[1], img1.shape[0]))
    return dxy[0][0], dxy[0][1], nimg2

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), 1)
    return cv_img


class imgfile():
    def __init__(self, name, path):
        self.name = name  # 文件名
        self.x = int(name.split('_')[0])  # 列号 横坐标
        self.y = int(name.split('_')[1].split('.')[0])  # 行号 纵坐标
        self.type = name.split('_')[1].split('.')[1]  # 文件类型
        self.img = cv_imread(os.path.join(path, name))


class imgdir:
    def __init__(self, path):
        self.path = path
        self.filelist=[]
        for filename in os.listdir(path):
            if not filename.find('.png') == -1:
                self.filelist.append(filename)

    def composite(self):
        xlist = []
        ylist = []
        imgtype = ''
        for name in self.filelist:
            imgfile1 = imgfile(name, self.path)
            if imgfile1.x not in xlist:
                xlist.append(imgfile1.x)
            if imgfile1.y not in ylist:
                ylist.append(imgfile1.y)
            imgtype = imgfile1.type
        xlist.sort()
        ylist.sort()
        imgcolumns = []
        imglist_all = []
        for x in xlist:
            imgrows = []
            imglist_row = []
            for y in ylist:
                imglist = os.path.join(self.path,
                                       str(x)+'_'+str(y)+'.'+imgtype)
                img = cv_imread(imglist)
                imgrows.append(img)
                imglist_row.append(str(x)+'_'+str(y)+'.'+imgtype)
            imgcolumn = np.vstack(imgrows)
            imgcolumns.append(imgcolumn)
            imglist_all.append(imglist_row)
        finalimg = np.hstack(imgcolumns)
        finallist = np.array(imglist_all)
        finallist = finallist.transpose(1, 0)
        return finalimg, finallist


def GetOverlapArea(jsonpath):
    """"""
    # 获取输入参数（输入文件夹、输出文件夹）
    jsonstring = json.loads(jsonpath)
    # 输入文件夹
    googleimgpath = jsonstring['inpath1']#待配准影像
    skybroundimgpath = jsonstring['inpath2']#标准影像
    skybroundmappath = jsonstring['inpath3']#标准地图
    inputpath1=inputpath(googleimgpath)
    inputpath2=inputpath(skybroundimgpath)
    inputpath3=inputpath(skybroundmappath)
    mainoutpath=inputpath1.mainpath
    mainoutpath2='matched'
    mainoutpath3=inputpath1.datasource+inputpath3.datasource+'对齐'





    # 输出文件夹
    ngoogleimgpath = '/'.join([mainoutpath,mainoutpath2,mainoutpath3,inputpath1.zoompath])
    nskybroundimgpath = '/'.join([mainoutpath,mainoutpath2,mainoutpath3,inputpath2.zoompath])
    nskybroundmappath = '/'.join([mainoutpath,mainoutpath2,mainoutpath3,inputpath3.zoompath])
    print (ngoogleimgpath,nskybroundimgpath,nskybroundmappath)
    for path in [ngoogleimgpath,nskybroundimgpath,nskybroundmappath]:
        if not os.path.exists(path):
            os.makedirs(path)
            print (path)
    # step1:拼接影像
    googlestitch = imgdir(googleimgpath)
    googleimg, googlelist = googlestitch.composite()
    skybroundstitch = imgdir(skybroundimgpath)
    skybroundimg, skybroundlist = skybroundstitch.composite()
    skybroundmapstitch = imgdir(skybroundmappath)
    meiyong, skybroundmaplist = skybroundmapstitch.composite()
    # step2:进行配准
    dx, dy, ngoogleimg = GetImageTranslation(skybroundimg, googleimg)
    print (dx,dy)
    # step3:寻找重叠区域
    rows, cols = googleimg.shape[0:2]
    print (rows,cols)
    xleftup = (dx if dx > 0 else 0)
    yleftup = (dy if dy > 0 else 0)
    xrightbottom = (cols+dx if cols+dx < cols else cols-1)
    yrightbottom = (rows+dy if rows+dy < rows else rows-1)
    print (xrightbottom,yrightbottom)
    # 寻找重叠区域对应瓦片
    irow, icol = googlelist.shape[0:2]
    i1 = (int(yleftup // 256 + 1) if yleftup > 0 else 0)
    j1 = (int(xleftup // 256 + 1) if xleftup > 0 else 0)
    i2 = int((rows - yrightbottom) // 256 + 1)
    j2 = int((cols - xrightbottom) // 256 + 1)
    print (i2,j2)
    # 根据最终重叠区域对谷歌影像进行裁剪
    nngoogleimg = ngoogleimg[i1*256:(irow-i2)*256, j1*256:(icol-j2)*256, :]
    # 筛选重叠区域瓦片对应文件名
    nskybroundlist = []
    nskybroundmaplist = []
    print (irow-i2,icol-j2)
    for i in range(i1, irow-i2):
        rowstr2 = []
        rowstr3 = []
        for j in range(j1, icol-j2):
            rowstr2.append(skybroundlist[i, j])
            rowstr3.append(skybroundmaplist[i, j])
        nskybroundlist.append(rowstr2)
        nskybroundmaplist.append(rowstr3)
    nskybroundlist = np.array(nskybroundlist)
    nskybroundmaplist = np.array(nskybroundmaplist)
    # 天地图结果复制到新文件夹、谷歌影像裁剪至新文件夹
    nirow, nicol = nskybroundlist.shape[0:2]
    for i in range(nirow):
        for j in range(nicol):
            cv2.imwrite(ngoogleimgpath + '/' + nskybroundlist[i, j],
                        nngoogleimg[i*256:(i+1)*256, j*256:(j+1)*256, :])
            copyfile(skybroundimgpath + '/' + nskybroundlist[i, j],
                     nskybroundimgpath + '/' + nskybroundlist[i, j])
            copyfile(skybroundmappath + '/' + nskybroundmaplist[i, j],
                     nskybroundmappath + '/' + nskybroundmaplist[i, j])

    nfilenamelist=[]
    for file in os.listdir(ngoogleimgpath):
        if not file.find('.png')==-1:
            nfilenamelist.append(file)
    pairpath='/'.join([mainoutpath,mainoutpath2,mainoutpath3,mainoutpath3,inputpath1.zoompath1]) 
    if not os.path.exists(pairpath):
        os.makedirs(pairpath)
    for file in nfilenamelist:
        img2=cv_imread(os.path.join(nskybroundmappath,file))
        img1=cv_imread(os.path.join(ngoogleimgpath,file))
        #img3=cv_imread(os.path.join(nskybroundimgpath,file))
        imgpair=np.hstack([img1,img2])
        cv2.imwrite(os.path.join(pairpath,file),imgpair)
        
    
        



if __name__=='__main__':
    # jsonstring = {'inpath1': r'F:\Chicago2\metadata\谷歌影像无标注\13\13_13aligned',
    #               'inpath2': r'F:\Chicago2\metadata\谷歌影像无标注\13\13_13aligned',
    #               'inpath3': r'F:\Chicago2\metadata\谷歌地图无标注\13\13_13aligned'}
    # jsonpath = json.dumps(jsonstring)

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json', type=str, help='输入json字符串')
    args = parser.parse_args()

    GetOverlapArea(args.input_json)











# rows, cols = googleimg.shape[0:2]
# xleftup = (dx if dx > 0 else 0)
# yleftup = (dy if dy > 0 else 0)
# xrightbottom = (cols+dx if cols+dx < cols else cols-1)
# yrightbottom = (rows+dy if rows+dy < rows else rows-1)
# # 寻找重叠区域对应瓦片
# irow = len(googlelist[0])
# icol = len(googlelist)
# i1 = (int(yleftup // 256 + 1) if yleftup > 0 else 0)
# j1 = (int(xleftup // 256 + 1) if xleftup > 0 else 0)
# i2 = int((rows - yrightbottom) // 256 + 1)
# j2 = int((cols - xrightbottom) // 256 + 1)
# # 根据最终重叠区域对谷歌影像进行裁剪
# nngoogleimg = ngoogleimg[i1*256:(irow-i2)*256, j1*256:(icol-j2)*256, :]
# # cv2.namedWindow('test', 0)
# # cv2.imshow('test', nngoogleimg)
# # cv2.waitKey(0)
# # 筛选重叠区域瓦片对应文件名
# nskybroundlist = []
# nskybroundmaplist = []
# for i in range(i1, irow-i2):
#     rowstr2 = []
#     rowstr3 = []
#     for j in range(j1, icol-j2):
#         rowstr2.append(skybroundlist[i][j])
#         rowstr3.append(skybroundmaplist[i][j])
#     nskybroundlist.append(rowstr2)
#     nskybroundmaplist.append(rowstr3)
# nskybroundlist = np.array(nskybroundlist)
# nskybroundmaplist = np.array(nskybroundmaplist)
# # 天地图结果复制到新文件夹
# nirow, nicol = nskybroundlist.shape[0:2]
# for i in range(nirow):
#     for j in range(nicol):
#         cv2.imwrite(ngoogleimgpath + '/' + nskybroundlist[i, j],
#                     nngoogleimg[i*256:(i+1)*256-1, j*256:(j+1)*256-1, :])
#         copyfile(skybroundimgpath + '/' + nskybroundlist[i, j],
#                  nskybroundimgpath + '/' + nskybroundlist[i, j])
#         copyfile(skybroundmappath + '/' + nskybroundmaplist[i, j],
#                  nskybroundmappath + '/' + nskybroundmaplist[i, j])
