# encoding:utf-8
"""
@OriginalAuthor: T.Xu
@Author: B.Yin
"""
from urllib import request
import urllib.request
import sys
import os
import math
import cv2
import numpy as np
import time
import random
import shutil
import json
import argparse
from coord_trans_utils import gcj02_to_wgs84, wgs84_to_gcj02


import osmnx as ox
import shapely#这个包单纯为了筛选geodataframe里面的geometry字段
agents = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1']

url_sources = [(
               'http://mt2.google.cn/vt/lyrs=m&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}&apistyle=s.t:0%3A3%7Cs.e%3Al.t%7Cp.v%3Aoff%2Cs.t%3A2%7Cp.v%3Aoff%2Cs.t%3A1%7Cs.e%3Al%7Cp.v%3Aoff%2Cs.t%3A5%7Cs.e%3Al%7Cp.v%3Aoff%2Cs.e%3Al%7Cp.v%3Aoff&style=api%7Csmartmaps',
               '谷歌地图无标注', 1), ('http://mt2.google.cn/vt/lyrs=m&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}', '谷歌地图有标注', 2), (
               'http://mt2.google.cn/vt/lyrs=h&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}&apistyle=s.t:0%3A3%7Cs.e%3Al.t%7Cp.v%3Aoff%2Cs.t%3A2%7Cp.v%3Aoff%2Cs.t%3A1%7Cs.e%3Al%7Cp.v%3Aoff%2Cs.t%3A5%7Cs.e%3Al%7Cp.v%3Aoff%2Cs.e%3Al%7Cp.v%3Aoff&style=api%7Csmartmaps',
               '谷歌路网无标注', 3), ('http://mt2.google.cn/vt/lyrs=h&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}', '谷歌路网有标注', 4),
               ('http://mt2.google.cn/vt/lyrs=t&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}', '谷歌地形图', 5),
               ('http://mt2.google.cn/vt/lyrs=r&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}', '谷歌地图无路网有标注', 6), (
               'http://mt2.google.cn/vt/lyrs=r&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}&apistyle=s.t:0%3A3%7Cs.e%3Al.t%7Cp.v%3Aoff%2Cs.t%3A2%7Cp.v%3Aoff%2Cs.t%3A1%7Cs.e%3Al%7Cp.v%3Aoff%2Cs.t%3A5%7Cs.e%3Al%7Cp.v%3Aoff%2Cs.e%3Al%7Cp.v%3Aoff&style=api%7Csmartmaps',
               '谷歌地图无路网无标注', 7), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=7&x={}&y={}&z={}&ltype=11',
               '高德地图无标注', 8), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=7&x={}&y={}&z={}&ltype=0',
               '高德地图有标注', 9), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=7&x={}&y={}&z={}&ltype=1',
               '高德地图去除水网路网无标注', 10), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=7&x={}&y={}&z={}&ltype=2',
               '高德地图路网水网无标注', 11), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=7&x={}&y={}&z={}&ltype=4',
               '高德地图标注图层', 12), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=8&x={}&y={}&z={}&ltype=3',
               '高德地图路网图层无标注', 13), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=8&x={}&y={}&z={}&ltype=4',
               '高德地图路网图层有标注', 14), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=8&x={}&y={}&z={}&ltype=3',
               '高德地图路网标注图层', 15), (
               'https://t0.tianditu.gov.cn/DataServer?T=vec_w&x={}&y={}&l={}&tk=44964a97c8c44e4d04efdf3cba594467',
               '天地图地图无标注', 16), (
               'https://t0.tianditu.gov.cn/DataServer?T=cva_w&x={}&y={}&l={}&tk=44964a97c8c44e4d04efdf3cba594467',
               '天地图地图标注图层', 17),
               ('http://mt2.google.cn/vt/lyrs=s&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}', 'GoogleSateNoLabel', 18),
               ('http://mt2.google.cn/vt/lyrs=y&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}', '谷歌影像有标注', 19), (
               'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scl=1&style=6&x={}&y={}&z={}&ltype=3',
               '高德影像无标注', 20), (
               'https://t0.tianditu.gov.cn/DataServer?T=img_w&x={}&y={}&l={}&tk=44964a97c8c44e4d04efdf3cba594467',
               '天地图影像无标注', 21), (
               'https://t0.tianditu.gov.cn/DataServer?T=cia_w&x={}&y={}&l={}&tk=44964a97c8c44e4d04efdf3cba594467',
               '天地图影像标注图层', 22), ('', 'OSM', 23)]

img_suffix = ".png"

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), 1)
    return cv_img


def cv_imwrite(filepath, img):
    cv2.imencode(img_suffix, img)[1].tofile(filepath)


def mk_zoom_dir(zoom, path):  # 创建层级文件夹，参数层级、上层文件夹路径（数据来源文件夹）
    zoompath = os.path.join(path, str(zoom))
    if not os.path.exists(zoompath):
        os.mkdir(zoompath)
    return zoompath

def mk_img_dir(zoom, x, path):  # 创建层级文件夹，参数层级、上层文件夹路径（数据来源文件夹）
    img_path = os.path.join(path, str(zoom), str(x))
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    return img_path    


def mkfolderaligned(zoomh, zooml, path):  # 创建最底层文件夹，参数高低层级、上层文件夹路径（数据来源文件夹）
    alignedpath = os.path.join(path, str(zooml) + '_' + str(zoomh) + 'aligned')
    if not os.path.exists(alignedpath):
        os.mkdir(alignedpath)
    return alignedpath


class ImgUrls(object):
    def __init__(self, url, mtype):  # url类，属性url和数据类型
        self.url = url
        self.type = mtype

    def mk_type_dir(self, mainpath):  # 创建数据来源文件夹，参数主存储路径
        typepath = os.path.join(mainpath, self.type)
        if not os.path.exists(typepath):
            os.mkdir(typepath)
        return typepath

    def gettpath(self, x, y, z):  # 获取单张图片下载地址
        tpath = self.url.format(x, y, z)
        return tpath


class MainDirTree(object):
    def __init__(self, path, sampleSetId):
        self.path = path  # 主存储路径
        self.sampleSetId = sampleSetId  # 样本集ID

    def mk_main_dir(self):
        mainpath = os.path.join(self.path, self.sampleSetId)
        if not os.path.exists(mainpath):
            os.mkdir(mainpath)
        return mainpath


class DataFile(object):
    def __init__(self, path, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.path = path  # 存储位置
        self.name = '{}{}'.format(y, img_suffix)  # 根据行列号得到文件名
        self.spath = os.path.join(self.path, self.name)
        self.zoom = z

    def getimg(self, Tpath):
        a = 0
        for a in range(0, 7):
            try:
                f = open(self.spath, 'wb')
                req = urllib.request.Request(Tpath)
                req.add_header('User-Agent', agents[a])  # 请求头循环8次
                pic = urllib.request.urlopen(req, timeout=60)
                f.write(pic.read())
                f.close()
                # print(str(self.x) + '_' + str(self.y) + ' downloading success', flush=True)
                break
            except Exception:
                print(str(self.x) + '_' + str(self.y) + ' downloading fail, retrying', flush=True)
                print('retrying' + str(a + 1), flush=True)
                continue


    def downloadflie(self, Tpath):
        if os.path.exists(self.spath):
            n = 0
            while n < 3:
                try:
                    im = cv_imread(self.spath)
                    conf_value = im.shape
                    # print(str(self.spath) + ' has been downloaded', flush=True)
                    n = 3
                except Exception:
                    print(str(self.spath) + ' cannot be read', flush=True)
                    os.remove(self.spath)
                    self.getimg(Tpath)
                    n = n + 1
        else:
            n = 0
            while n < 3:
                self.getimg(Tpath)
                try:
                    im = cv_imread(self.spath)
                    conf_value = im.shape
                    # print(str(self.spath) + ' has been downloaded', flush=True)
                    n = 3
                except Exception:
                    print(str(self.spath) + ' cannot be read', flush=True)
                    os.remove(self.spath)
                    self.getimg(Tpath)
                    n = n + 1

    def combinationxandy(self, zoomh):
        t = int(2 ** (int(zoomh) - int(self.zoom)))
        xbegin = self.x * t
        ybegin = self.y * t
        xend = (self.x + 1) * t
        yend = (self.y + 1) * t
        xrange = list(range(xbegin, xend))
        yrange = list(range(ybegin, yend))
        return xrange, yrange


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


class XnYTile(object):
    def __init__(self, type, parameter):
        if type == 'coordinate':
            self.lat_deg1 = parameter[0]
            self.lon_deg1 = parameter[1]
            self.lat_deg2 = parameter[2]
            self.lon_deg2 = parameter[3]

    def xandyrange(self, zoom):
        lefttop = deg2num(self.lat_deg1, self.lon_deg1, zoom)
        rightbottom = deg2num(self.lat_deg2, self.lon_deg2, zoom)
        xrange = list(range(lefttop[0], rightbottom[0] + 1))
        yrange = list(range(lefttop[1], rightbottom[1] + 1))
        return xrange, yrange

class MainFunc(object):
    def __init__(self, zoom_list, mainpath, sampleSetId, coordinates, tileSources):
        self.zoom_list = zoom_list
        self.mainpath = mainpath
        self.sampleSetId = sampleSetId
        self.coordinates = coordinates
        self.tileSources = tileSources

    def donwloadingandsave(self):
        try:
            print("Begin download tiles")
            mdtree = MainDirTree(self.mainpath, self.sampleSetId)
            maindirs = mdtree.mk_main_dir()

            print("self.coordinates:", self.coordinates)

            xandytile1 = XnYTile('coordinate', self.coordinates)
            zoomlist1 = self.zoom_list

            for source in self.tileSources:
                imgurl = ImgUrls(url_sources[source][0], url_sources[source][1])
                source = imgurl.mk_type_dir(maindirs)
                for zoom in self.zoom_list:
                    zoom_dir = mk_zoom_dir(zoom, source)  # 生成层级文件夹

                    for x, y in zip(xandytile1.xandyrange(zoom)[0], xandytile1.xandyrange(zoom)[1]):
                        
                        if False:#source in [19]:
                            new_x, new_y = wgs84_to_gcj02(x, y)
                            print("校正ing", new_x, new_y, x, y)
                        else:
                            new_x, new_y = x, y

                        img_dir = mk_img_dir(zoom, x, source)
                        datafile1 = DataFile(img_dir, x, y, zoom)
                        datafile1.downloadflie(imgurl.gettpath(new_x, new_y, zoom))
                    # for p in new_coords:  # 下载多层级元数据
                    #     x = p[0]
                    #     img_dir = mk_img_dir(zoom, x, source)
                    #     for p in new_coords:
                    #         y = p[1]
                    #         datafile1 = DataFile(img_dir, x, y, zoom)
                    #         datafile1.downloadflie(imgurl.gettpath(x, y, zoom))
            print("SUCCESS")
        except Exception as e:
            print(e)
           

def osmdl(TYPES,coordinates,mainpath,sampleSetId):
    path=os.path.join(mainpath,sampleSetId,'OSM')
    if not os.path.exists(path):
        os.mkdir(path)
    lefttop_lat_deg = coordinates[0]
    lefttop_lon_deg = coordinates[1]
    rightbottome_lat_deg = coordinates[2]
    rightbottome_lon_deg = coordinates[3]

    north = lefttop_lat_deg
    south = rightbottome_lat_deg
    east = rightbottome_lon_deg
    west = lefttop_lon_deg
    
    print ('Begin downloading OSM data of'+str((north,south,east,west)), flush=True)
    try:
        for TYPE in TYPES:
            if TYPE == 'road':
                G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
                if not os.path.exists(os.path.join(path,'road')):
                    os.makedirs(os.path.join(path,'road'))
                ox.io.save_graph_shapefile(G, filepath=os.path.join(path,'road/'), encoding='utf-8')
            else:
                gdf = ox.geometries.geometries_from_bbox(north, south, east, west, tags={TYPE:True}) 
                typepath = os.path.join(path,'%s' % (TYPE))
                if not os.path.exists(typepath):
                    os.makedirs(typepath)
                gdf = gdf[['nodes', TYPE, 'name', 'geometry']]
                gdf_save = gdf.applymap(lambda x: str(x) if isinstance(x, list) else x)
                polygonindex=[]
                for i,v in gdf_save['geometry'].items():
                    if not isinstance(v,shapely.geometry.polygon.Polygon):#筛掉不是polygon类型的记录，不然类型混杂不能保存到shapefile
                        polygonindex.append(i) 
                gdf_save=gdf_save.drop(polygonindex)
                gdf_save.drop(labels='nodes', axis=1).to_file(os.path.join(path,'%s/%s.shp' % (TYPE, TYPE)), driver='Shapefile')
        print("SUCCESS")
    except Exception:
        print("ERROR")


def takejson(getjson):
    json_obj = json.loads(getjson)
    mainpath = json_obj["mainpath"]
    sampleSetId = json_obj["sampleSetId"]
    coordinates = json_obj["coordinates"]
    vectorSource = json_obj["vectorSource"]
    tileSources = [json_obj["tileSource"]]
    zoom_list = json_obj["zoomlist"]
    TYPES = json_obj["types"]
    index_list = []
    for index in range(0, 23):
        index_list.append(index) 
    samplesetpath = os.path.join(mainpath, sampleSetId)
    if not os.path.exists(samplesetpath):
        os.mkdir(samplesetpath)
    if vectorSource == 0:
        osmdl(TYPES,coordinates,mainpath,sampleSetId) # 下载矢量数据    
    if json_obj["tileSource"] in index_list: #下载影像数据
        mainfunction1 = MainFunc(zoom_list, mainpath, sampleSetId, coordinates, tileSources)
        mainfunction1.donwloadingandsave()      

if __name__ == "__main__":
    zoom_list = []
    for zoom in range(1, 23):
        zoom_list.append(zoom)
    jsonstring = {
        "mainpath": "/scripts", #挂载路径
        "sampleSetId": sys.argv[1], #样本集ID
        "coordinates": [
            float(sys.argv[2]), #纬度上边界
            float(sys.argv[3]), #经度左边界
            float(sys.argv[4]), #纬度下边界
            float(sys.argv[5])],#经度右边界
        "tileSource": int(sys.argv[6]), #下载影像的数据源
        "vectorSource":int(sys.argv[7]), #下载矢量的数据源
        "types": sys.argv[8].split(','),
        "zoomlist": zoom_list,
    }
    json1 = json.dumps(jsonstring)
    takejson(json1)
