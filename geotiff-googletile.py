from osgeo import gdal
import os
import numpy as np
import cv2
import json

def cv_imread(file_path):
    cv_img=cv2.imdecode(np.fromfile(file_path,dtype=np.uint8),-1)
    return cv_img

def readtif(path):
    dataset=gdal.Open(path)
    #print (type(dataset))
    #print (dataset)
    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    print (im_geotrans)
    print (im_proj)
    return (im_proj)

class maptile:
    def __init__(self,dir,name):
        self.path=os.path.join(dir,name)
        name1=name.split('.')[0]
        self.x=int(name1.split('_')[0])
        self.y=int(name1.split('_')[1])
        self.img=cv_imread(self.path)
        print (self.img.shape)
        self.b=cv2.split(self.img)[0]
        self.g = cv2.split(self.img)[1]
        self.r = cv2.split(self.img)[2]
        zooms=dir.split(os.sep)[-1]
        self.zooml=int(zooms.split('_')[0])
        self.zoomh=int(zooms.split('_')[1].split('aligned')[0])
        xrange = 20037508.3427892 * 2
        n=2**self.zoomh*256
        m=2**self.zooml
        self.trans0=-20037508.3427892+self.x*20037508.3427892*2/m
        self.trans1=xrange/n
        self.trans2=0
        self.trans3=20037508.3427892-self.y*20037508.3427892*2/m
        self.trans4=0
        self.trans5=-xrange/n
        self.trans=[self.trans0,self.trans1,self.trans2,self.trans3,self.trans4,self.trans5]
        self.proj='PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]'




    def writeinfo(self):
        dataset=gdal.Open(self.path)
        im_width=dataset.RasterXSize
        im_height=dataset.RasterYSize
        print (im_width,im_height)
        #print (im_bands)
        driver = gdal.GetDriverByName("GTiff")
        file=self.path.replace('.png','.tif')
        dataset = driver.Create(file, im_width, im_height, 3, gdal.GDT_Byte)
        dataset.SetProjection(self.proj)
        #xrange=20037508.3427892*2
        dataset.SetGeoTransform(self.trans)
        #print (dataset.GetRasterBand(0))
        dataset.GetRasterBand(1).WriteArray(self.r)
        dataset.GetRasterBand(2).WriteArray(self.g)
        dataset.GetRasterBand(3).WriteArray(self.b)


def takejson(getjson):
    jsonstring=json.loads(getjson)
    path=jsonstring['path']
    filelist=os.listdir(path)
    for file in filelist:
        maptile1=maptile(path,file)
        maptile1.writeinfo()
        readtif(maptile1.path.replace('.png','.tif'))

class xyz:
    def __init__(self,x,y,z):#原理就是假设将地球映射到一个长宽均为xrange的正方形，然后将其按层级z划分为2**Z个小正方形
        self.x=x
        self.y=y
        self.z=z
        xrange = 20037508.3427892 * 2#世界地图对应的实际长宽为多少米
        n = 2 ** self.z * 256#世界地图长（宽）多少像素值
        m = 2 ** self.z#世界地图多少行（列）
        self.trans0 = -20037508.3427892 + self.x * 20037508.3427892 * 2 / m#左上角大地横坐标
        self.trans1 = xrange / n#每像素的x轴偏移量
        self.trans2 = 0
        self.trans3 = 20037508.3427892 - self.y * 20037508.3427892 * 2 / m#左上角大地纵坐标
        self.trans4 = 0
        self.trans5 = -xrange / n#每像素的y轴偏移量
        self.tfwlines=[str(self.trans1)+'\n',str(self.trans2)+'\n',str(self.trans4)+'\n',str(self.trans5)+'\n',str(self.trans0)+'\n',str(self.trans3)+'\n',]


    def writetfw(self,path):
        f=open(path,'w')
        print (self.tfwlines)
        f.writelines(self.tfwlines)
        f.close()


if __name__=='__main__':
    #给文件夹用的版本，文件夹会遍历所有图片然后将所有图片转成geotiff
    #json1={'path':r'F:\googleglobal1-7\metadata\谷歌地图无标注\0\0_1aligned'}
    #json1=json.dumps(json1)
    #takejson(json1)
    #给单张图片用的版本，用左上角第一张瓦片命名
    #maptile1=maptile(r'C:\Users\Sweetday\Desktop\15_15aligned','27420_13378.png')
    #maptile1.writeinfo()
    #给图片信息用的版本，x_y用文件名或者文件夹里面的xmin ymin
    xyz1=xyz(27420,13378,15)
    xyz1.writetfw(r'C:\Users\Sweetday\Desktop\27420_13378.tfw')#google和高德这样做geoserver还是识别不了，因为要识别大地坐标必须要有proj4字符串
