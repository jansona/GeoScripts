# 数据预处理 阴影过滤
#yangzhen
#2020.4.13
#translate from matlab
"""get the shadow proportion from images 
   of remote sensing"""
import numpy as np
import cv2
import os
import json
from shutil import copyfile
import argparse

def cv_imread(file_path):
    cv_img=cv2.imdecode(np.fromfile(file_path,dtype=np.uint8),1)
    return cv_img

def cv_imwrite(filepath,img):
    cv2.imencode(".png",img)[1].tofile(filepath)

def standard(data):
    '''影像文件标准化
       输入单通道影像
       输出标准化后单通道影像'''
    mdata = data.copy()
    irow, icol = mdata.shape[0:2]
    mdata = np.reshape(mdata, [irow*icol, 1])
    temp1 = mdata - np.min(data)
    result = temp1/(np.max(data)-np.min(data))
    result = np.reshape(result, [irow, icol])
    np.seterr(divide='ignore', invalid='ignore')
    return result

def GetLight(img):
    '''计算人眼视觉特性亮度'''
    mimg = img.copy()
    B = mimg[:,:,0]
    G = mimg[:,:,1]
    R = mimg[:,:,2]
    result = 0.04*R+0.5*G+0.46*B
    return result

def GetColor(img):
    '''色度空间归一化'''
    mimg = img.copy()
    misc = mimg[:,:,0]+mimg[:,:,1]+mimg[:,:,2]
    misc[misc == 0] = 0.0000001
    mimg[:,:,0] = img[:,:,0]/misc
    mimg[:,:,1] = img[:,:,1]/misc
    result = np.abs(mimg - img)
    result = (result[:,:,0]+result[:,:,1])/2
    return result

def GetVege(img):
    '''获取植被特征'''
    mimg = img.copy()
    B = mimg[:,:,0]
    G = mimg[:,:,1]
    R = mimg[:,:,2]
    result = G-np.minimum(R, B)
    result[result<0] = 0
    return result

def GetLDV(idist, ilight, ivege):
    '''总决策'''
    idist = standard(idist)
    ilight = standard(ilight)
    ivege = standard(ivege)
    result = idist-ilight-ivege
    result[result<0]=0
    return result

def FinalTrare(img):
    '''结果后处理'''
    mimg = img.copy()
    mimg = np.uint8(standard(mimg)*255)
    T, result = cv2.threshold(mimg, 0, 255, cv2.THRESH_OTSU)
    result = cv2.medianBlur(result, 7)
    return result



def ShadowsProportion(path:{}):
    """
       阴影提取
       @@path: {}, 
       @path[0] 待检测阴影的影像
       @path[1] 待检测阴影的影像
       @path[2]  阴影比例阈值
       ps: 当两张影像过大时会进行分块
    """
    File_in = path[0] 
    File_out = path[1] 
    T = path[2]
    mpath = path[3]
    File_out2=path[4]
    if not os.path.exists(File_out):
        os.makedirs(File_out)
    if not os.path.exists(File_out2):
        os.makedirs(File_out2)
    #开始检测
    namelist=[]
    for filename in os.listdir(File_in):
        if not filename.find('.png') == -1:
            namelist.append(filename)
    n = len(namelist)
    fid = open('ShadowsProportion.txt', 'w')
    for i in range(n):
        filenamein = os.path.join(File_in, namelist[i])
        img = cv_imread(filenamein)
        #获取阴影
        img1 = img.astype(np.float)
        img1[:,:,0] = standard(img[:,:,0])
        img1[:,:,1] = standard(img[:,:,1])
        img1[:,:,2] = standard(img[:,:,2])
        idist = GetColor(img1)
        ilight = GetLight(img1)
        ivege = GetVege(img1)
        final = GetLDV(idist, ilight, ivege)
        shadow = FinalTrare(final)
        shadow = shadow/255
        #计算阴影比例并保存比例值
        S = shadow.size
        s = np.sum(sum(shadow))
        iratio = s/S
        fid.write(namelist[i] + ',' + str('%.3f' % iratio) + '\n')
        #保存阴影比例小于阈值的图片
        filenameout = os.path.join(File_out, namelist[i])
        filenameout2 = os.path.join(File_out2, namelist[i])
        mapout = mpath.replace('metadata','noshade')
        if not os.path.exists(mapout):
            os.makedirs(mapout)
        if iratio < T:
            cv_imwrite(filenameout, img)
            copyfile(os.path.join(mpath,namelist[i]),(os.path.join(mapout,namelist[i])))
        else :
            cv_imwrite(filenameout2, img)
    fid.close()


def takejson(getjson):
    json1 = json.loads(getjson)

    path = {}
    path[0] = json1['rpath']
    path[1] = path[0].replace('metadata','noshade')
    path[2] = json1['shadowProportion']
    path[3]=json1['mpath']
    path[4]=path[0].replace('metadata','withshade')
    #print (path)
    ShadowsProportion(path)

    print ('Shadow filtering Completed')

if __name__ == "__main__":
    #获取输入图片路径，阴影比例阈值，输出图片路径
    # File_in = input('Please input the data file name:')
    # T = float(input('Please input the  threshold value:'))
    # File_out = input('Please input the out-img filename:')

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json', type=str, help='输入json字符串')
    args = parser.parse_args()

    # json1={'rpath':r'F:\Chicago2\metadata\谷歌影像无标注\14\14_14aligned','mpath':r'F:\Chicago2\metadata\谷歌地图无标注\14\14_14aligned','shadowProportion':0.2}
    # getjson=json.dumps(json1)
    takejson(args.input_json)

