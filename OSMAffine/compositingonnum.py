import os
import cv2
import numpy as np
import json

def cv_imread(file_path):
    cv_img=cv2.imdecode(np.fromfile(file_path,dtype=np.uint8),-1)
    return cv_img

def cv_imwrite(filepath,img):
    cv2.imencode(".tif",img)[1].tofile(filepath)

class imgfile():
    def __init__(self,name,path):
        self.name=name#文件名
        self.x=int(name.split('_')[0])#列号 横坐标
        self.y=int(name.split('_')[1].split('.')[0])#行号 纵坐标
        self.type=name.split('_')[1].split('.')[1]#文件类型
        self.img=cv_imread(os.path.join(path,name))


class imgdir:
    def __init__(self,path):
        self.path=path
        self.filelist=os.listdir(path)

    def composite(self):
        xlist=[]
        ylist=[]
        imgtype=''
        for name in self.filelist:
            imgfile1=imgfile(name,self.path)
            if not imgfile1.x in xlist:
                xlist.append(imgfile1.x)
            if not imgfile1.y in ylist:
                ylist.append(imgfile1.y)
            imgtype=imgfile1.type
        #xlist.sort()
        #ylist.sort()
        imgcolumns=[]
        #print (max(xlist),max(ylist))
        x=min(xlist)
        while x <= max(xlist):
            imgrows=[]
            y=min(ylist)

            while y <= max(ylist):
                img=cv_imread(os.path.join(self.path,str(x)+'_'+str(y)+'.'+imgtype))
                imgrows.append(img)
                y=y+1
            imgcolumn=np.vstack(imgrows)
            imgcolumns.append(imgcolumn)
            x=x+1
        finalimg=np.hstack(imgcolumns)
        return finalimg


def takejson(getjson):
    json1=json.loads(getjson)
    path1=json1['remotepath']
    path2=json1['mappath']
    cachepath=json1['Cachepath']
    if not os.path.exists(cachepath):
        os.makedirs(cachepath)
    imgdir1=imgdir(path1)
    imgdir2 = imgdir(path2)
    finalimg1=imgdir1.composite()
    finalimg2=imgdir2.composite()
    rmpath=os.path.join(cachepath,'rm.png')
    mappath=os.path.join(cachepath,'map.png')
    cv_imwrite(rmpath,finalimg1)
    cv_imwrite(mappath, finalimg2)
    return (rmpath,mappath)

'''
if __name__=="__main__":
    jsonstring={'path1':r'F:\taizhong\metadata\谷歌影像无标注\17\17_17aligned'}#,'path2':r'F:\Shanghaitest2tif\metadata\高德影像无标注\17\17_17aligned'}#,'mappath':''}
    json1=json.dumps(jsonstring)
    takejson(json1)
'''