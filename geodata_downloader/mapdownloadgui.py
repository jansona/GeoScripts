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

# import osmnx as ox

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
               'GoogleMapNoLabel', 1), ('http://mt2.google.cn/vt/lyrs=m&scale=1&hl=zh-CN&gl=cn&x={}&y={}&z={}', '谷歌地图有标注', 2), (
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
    def __init__(self, path, name):
        self.path = path  # 主存储路径
        self.name = name  # 数据集名称

    def keep_coordinate(self, lat_deg1, lon_deg1, lat_deg2, lon_deg2):
        filename = str(time.time()) + '.txt'
        coordinatefile = open(os.path.join(self.path, self.name, filename), 'w')
        coordinatefile.write(
            'lefttop lat_deg:' + str(lat_deg1) + ' lon_deg:' + str(lon_deg1) + '\n' + 'rightbottome lat_deg:' + str(
                lat_deg2) + ' lon_deg:' + str(lon_deg2))
        coordinatefile.close()

    def mkdirs(self):
        mainpath = os.path.join(self.path, self.name)
        if not os.path.exists(mainpath):
            os.mkdir(mainpath)
        path1 = os.path.join(mainpath, 'metadata')
        if not os.path.exists(path1):
            os.mkdir(path1)
        path2 = os.path.join(mainpath, 'datasets')
        if not os.path.exists(path2):
            os.mkdir(path2)
        return path1, path2


class DataFile(object):
    def __init__(self, path, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.path = path  # 存储位置
        self.name = '{}_{}{}'.format(x, y, img_suffix)  # 根据行列号得到文件名
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
                print(str(self.x) + '_' + str(self.y) + ' downloading success')
                # print(threading.currentThread().getName())
                break
            except Exception:
                print(str(self.x) + '_' + str(self.y) + ' downloading fail,retrying')
                print('retrying' + str(a + 1))
                continue

    def downloadflie(self, Tpath):
        if os.path.exists(self.spath):
            n = 0
            while n < 3:
                try:
                    im = cv_imread(self.spath)
                    conf_value = im.shape
                    print(str(self.spath) + 'has been downloaded')
                    n = 3
                except Exception:
                    print(str(self.spath) + 'cannot be read')
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
                    print(str(self.spath) + ' has been downloaded')
                    n = 3

                except Exception:
                    print(str(self.spath) + ' cannot be read')
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
    print(xtile, ytile)
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
        print(str(lefttop[0]))
        print(str(rightbottom[0]))
        print(str(lefttop[1]))
        print(str(rightbottom[1]))
        print("共" + str(rightbottom[0] - lefttop[0] + 1))
        print("共" + str(rightbottom[1] - lefttop[1] + 1))
        xrange = list(range(lefttop[0], rightbottom[0] + 1))
        yrange = list(range(lefttop[1], rightbottom[1] + 1))
        return xrange, yrange


class ZoomList(object):
    def __init__(self, zoomhlist, zoomllist):
        self.zoomhs = zoomhlist
        self.zoomls = zoomllist
        self.zooms = set.union(set(self.zoomls), set(self.zoomhs))
        self.zoomin = min(self.zooms)


class TrainAndTestDir(object):
    def __init__(self, path, mappath, dpath):
        self.path = path  # 遥感影像目录
        self.filelist = os.listdir(path)
        self.fileamount = len(self.filelist)
        self.mappath = mappath  # 对应瓦片目录
        self.dpath = dpath

    def classify(self, ratioofdataset):
        n1 = int(self.fileamount * (ratioofdataset[0] / (sum(ratioofdataset) + ratioofdataset[2])))
        testlist = random.sample(self.filelist, n1)
        alltrainlist = set(self.filelist).symmetric_difference(testlist)
        n = int(len(alltrainlist) * (ratioofdataset[1] / (ratioofdataset[1] + ratioofdataset[2] * 2)))
        print(n)
        trainlist = random.sample(alltrainlist, n)
        unpairlist = set(alltrainlist).symmetric_difference(trainlist)
        trainAlist = random.sample(unpairlist, int(len(unpairlist) / 2))
        print(len(trainAlist))
        trainBlist = random.sample(unpairlist.symmetric_difference(set(trainAlist)), len(trainAlist))
        print(len(trainBlist))
        return trainlist, trainAlist, trainBlist, testlist

    def mktest(self, testlist):
        imgdpath = os.path.join(self.dpath, 'testA')
        if not os.path.exists(imgdpath):
            os.mkdir(imgdpath)
        mapdpath = os.path.join(self.dpath, 'testB')
        if not os.path.exists(mapdpath):
            os.mkdir(mapdpath)
        for map in testlist:
            shutil.copyfile(os.path.join(self.path, map), os.path.join(imgdpath, map))
            shutil.copyfile(os.path.join(self.mappath, map), os.path.join(mapdpath, map))

    def madetrain(self, trainlist):
        for map_name in trainlist:
            print(self.mappath + map_name)
            rightimg = cv_imread(os.path.join(self.mappath, map_name))
            print(np.shape(rightimg))
            leftimg = cv_imread(os.path.join(self.path, map_name))
            print(np.shape(leftimg))
            img = np.hstack([leftimg, rightimg])
            trainpath = os.path.join(self.dpath, 'train')
            if not os.path.exists(trainpath):
                os.mkdir(trainpath)
            cv_imwrite(os.path.join(trainpath, map_name), img)

    def make_trainA_trainB(self, trainAlist, trainBlist):
        for img in trainAlist:
            dpathA = os.path.join(self.dpath, 'trainA')
            if not os.path.exists(dpathA):
                os.mkdir(dpathA)
            shutil.copyfile(os.path.join(self.path, img), os.path.join(dpathA, img))
        for map_name in trainBlist:
            dpathB = os.path.join(self.dpath, 'trainB')
            if not os.path.exists(dpathB):
                os.mkdir(dpathB)
            shutil.copyfile(os.path.join(self.mappath, map_name), os.path.join(dpathB, map_name))


def compositing(Spath, Tpath, xandyrange, zoom, filename):
    try:
        imrow = []
        for x in xandyrange[0]:
            imcolumn = []
            for y in xandyrange[1]:
                im = cv_imread(os.path.join(Spath, '{}_{}{}'.format(x, y, img_suffix)))
                imcolumn.append(im)
            imstripe = np.vstack(imcolumn)
            imrow.append(imstripe)
        imwhole = np.hstack(imrow)
        cv_imwrite(os.path.join(Tpath, filename), imwhole)
        print('Finish composite' + filename + ' of zoom{}'.format(zoom))
    except Exception:
        print('Cannot composite' + filename + ' of zoom{}'.format(zoom))


class MainFunc(object):
    def __init__(self, zoomhlist, zoomllist, mainpath, datasetname, coordinates, datasources):
        self.zoomhlist = zoomhlist
        self.zoomllist = zoomllist
        self.mainpath = mainpath
        self.datasetname = datasetname
        self.coordinates = coordinates
        self.datasources = datasources

    def donwloadingandsave(self):
        mdtree = MainDirTree(self.mainpath, self.datasetname)
        maindirs = mdtree.mkdirs()
        xandytile1 = XnYTile('coordinate', self.coordinates)
        # mdtree.keepcoordinate(xandytile1.lat_deg1, xandytile1.lon_deg1, xandytile1.lat_deg2, xandytile1.lon_deg2)
        zoomlist1 = ZoomList(self.zoomhlist, self.zoomllist)
        for source in self.datasources:
            imgurl = ImgUrls(url_sources[source][0], url_sources[source][1])
            typedir = imgurl.mk_type_dir(maindirs[0])
            zoomindir = mk_zoom_dir(zoomlist1.zoomin, typedir)  # 生成最低层级文件夹
            zoominaligneddir = mkfolderaligned(zoomlist1.zoomin, zoomlist1.zoomin, zoomindir)  # 生成最低层级256瓦片文件夹
            for x in xandytile1.xandyrange(zoomlist1.zoomin)[0]:  # 下载多层级元数据
                for y in xandytile1.xandyrange(zoomlist1.zoomin)[1]:
                    datafile1 = DataFile(zoominaligneddir, x, y, zoomlist1.zoomin)
                    datafile1.downloadflie(imgurl.gettpath(x, y, zoomlist1.zoomin))
                    for zoom in zoomlist1.zooms:
                        if not zoom == zoomlist1.zoomin:
                            combinationxandy1 = datafile1.combinationxandy(zoom)
                            zoomdir = mk_zoom_dir(zoom, typedir)  # 生成其他层级文件夹
                            zoomaligneddir = mkfolderaligned(zoom, zoom, zoomdir)  # 生成其他层级256*256瓦片底图文件夹
                            for a in combinationxandy1[0]:
                                for b in combinationxandy1[1]:
                                    datafile2 = DataFile(zoomaligneddir, a, b, zoom)
                                    datafile2.downloadflie(imgurl.gettpath(a, b, zoom))

            for zoomh in self.zoomhlist:  # 对齐拼合多层级数据
                for zooml in self.zoomllist:
                    if zooml < zoomh:
                        zoomldir = mk_zoom_dir(zooml, typedir)
                        zoomhdir = mk_zoom_dir(zoomh, typedir)
                        zoomlaligneddir = mkfolderaligned(zooml, zooml, zoomldir)
                        Spath = mkfolderaligned(zoomh, zoomh, zoomhdir)
                        Tpath = mkfolderaligned(zoomh, zooml, zoomldir)
                        filelist1 = os.listdir(zoomlaligneddir)
                        for filename in filelist1:
                            x = filename.split('_')[0]
                            y = filename.split('_')[1].rstrip(img_suffix)
                            datafile2 = DataFile(zoomlaligneddir, x, y, zooml)
                            xandyrange = datafile2.combinationxandy(zoomh)
                            compositing(Spath, Tpath, xandyrange, zoomh, filename)


'''
def osmdl(TYPES,coordinates,mainpath,datasetname):
    path=os.path.join(mainpath,datasetname,'OSM')
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

    for TYPE in TYPES:
        gdf = ox.footprints.footprints_from_point(north, south, east, west, footprint_type="%s" % (TYPE)) #
        typepath = os.path.join(path,'%s' % (TYPE))

        if not os.path.exists(typepath):
            os.makedirs(typepath)

        gdf = gdf[['nodes', TYPE, 'name', 'geometry']]
        gdf_save = gdf.applymap(lambda x: str(x) if isinstance(x, list) else x)
        gdf_save.drop(labels='nodes', axis=1).to_file(os.path.join(path,'%s/%s.shp' % (TYPE, TYPE)), driver='Shapefile')

    G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    if not os.path.exists(os.path.join(path,'road')):
        os.makedirs(os.path.join(path,'road'))

    ox.io.save_graph_shapefile(G, filepath=os.path.join(path,'road/'), encoding='utf-8')
    G_projected = ox.project_graph(G)
    ox.plot_graph(G_projected)
'''


def takejson(getjson):
    json_obj = json.loads(getjson)
    mainpath = json_obj["mainpath"]
    datasetname = json_obj["datasetname"]
    coordinates = json_obj["coordinates"]
    datasetpath = os.path.join(mainpath, datasetname)
    if not os.path.exists(datasetpath):
        os.mkdir(datasetpath)
    filename = str(time.time()) + '.txt'
    coordinatefile = open(os.path.join(datasetpath, filename), 'w')
    coordinatefile.write(
        'lefttop lat_deg:' + str(coordinates[0]) + ' lon_deg:' + str(
            coordinates[1]) + '\n' + 'rightbottome lat_deg:' + str(
            coordinates[2]) + ' lon_deg:' + str(coordinates[3]))
    coordinatefile.close()

    for data in json_obj["datas"]:
        if not data["datasource"] == 23:
            datasources = [data["datasource"]]
            zoomllist = [data["zooml"]]
            zoomhlist = data["zoomhlist"]
            mainfunction1 = MainFunc(zoomhlist, zoomllist, mainpath, datasetname, coordinates, datasources)
            mainfunction1.donwloadingandsave()
        else:
            pass
            #TYPES = data["TYPE"]
            # osmdl(TYPES,coordinates,mainpath,datasetname)


if __name__ == "__main__":
    # ratioofdataset=[1,3,3]#int list,test,pair,unpair’s ratio
    # mainfunction1=mainfunction(zoomhlist,zoomllist,mainpath,datasetname,coordinates,datasources)
    # mainfunction1.donwloadingandsave(ratioofdataset)
    # jsonstring={
    #     "mainpath":"/data02/data_download/", "datasetname":"Toronto", 
    #     "coordinates":[43.813320, -79.533858,43.693622, -79.275761],
    #     "datas":[{"datasource":0, 'zooml':13,'zoomhlist':[13,14]}]}
    with open(sys.argv[1], 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    json_str = ' '.join(lines)
    # json1=json.dumps(jsonstring)
    takejson(json_str)
