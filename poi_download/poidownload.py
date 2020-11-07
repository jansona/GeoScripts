# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 18:33:57 2020

@author: sqz
"""

from urllib.parse import quote
import json
import sys
import os
import time
import collections
import pandas as pd
from requests.adapters import HTTPAdapter
import requests
import math
import numpy as np
import csv
import osmnx as ox
import cv2
from shutil import copyfile
import hashlib
#from shp import trans_point_to_shp


'''
版本更新说明：
2020.06.19:
    1.
'''
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率
#################################################需要修改###########################################################

## TODO 1.划分的网格距离，0.02-0.05最佳，建议如果是数量比较多的用0.01或0.02，如餐厅，企业。数据量少的用0.05或者更大，如大学
pology_split_distance = 0.02

## TODO 2. 城市编码，参见高德城市编码表，注意需要用adcode列的编码(不重要)
city_code = '150100'


## TODO 3. 高德开放平台密钥
gaode_key = ['Web_APP_Key_GaoDeMap']

# TODO 4.输出数据坐标系,1为高德GCJ20坐标系，2WGS84坐标系，3百度BD09坐标系
coord = 2

############################################以下不需要动#######################################################################


poi_pology_search_url = 'https://restapi.amap.com/v3/place/polygon'

buffer_keys = collections.deque(maxlen=len(gaode_key))

def cv_imread(file_path):
    cv_img=cv2.imdecode(np.fromfile(file_path,dtype=np.uint8),1)
    return cv_img

def cv_imwrite(filepath,img):
    cv2.imencode(".png",img)[1].tofile(filepath)
def generate_grids(start_long,start_lat,end_long,end_lat,resolution):
    """
    根据起始的经纬度和分辨率，生成需要需要的网格.
    方向为左上，右下，所以resolution应为 负数，否则未空
    :param start_long:
    :param start_lat:
    :param end_long:
    :param end_lat:
    :param resolution:
    :return:
    """
    assert start_long < end_long,'需要从左上到右下设置经度，start的经度应小于end的经度'
    assert start_lat > end_lat,'需要从左上到右下设置纬度，start的纬度应大于end的纬度'
    assert resolution>0,'resolution应大于0'


    grids_lib=[]
    longs = np.arange(start_long,end_long,resolution)
    if longs[-1] != end_long:
        longs = np.append(longs,end_long)

    lats = np.arange(start_lat,end_lat,-resolution)
    if lats[-1] != end_lat:
        lats = np.append(lats,end_lat)
    for i in range(len(longs)-1):
        for j in range(len(lats)-1):
            grids_lib.append([round(float(longs[i]),6),round(float(lats[j]),6),round(float(longs[i+1]),6),round(float(lats[j+1]),6)])
            #yield [round(float(longs[i]),6),round(float(lats[j]),6),round(float(longs[i+1]),6),round(float(lats[j+1]),6)]
    return grids_lib

def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]

def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def init_queen():
    for i in range(len(gaode_key)):
        buffer_keys.append(gaode_key[i])
    print('当前可供使用的高德密钥：', buffer_keys)


# 根据grid和分类关键字获取poi数据
def getpois(grids, keywords):
    if buffer_keys.maxlen == 0:
        print('密钥已经用尽，程序退出！！！！！！！！！！！！！！！')
        exit(0)
    amap_key = buffer_keys[0]  # 总是获取队列中的第一个密钥

    i = 1
    poilist = []
    while True:  # 使用while循环不断分页获取数据
        result = getpoi_page(grids, keywords, i, amap_key)
        #print(result)
        if result != None:
            result = json.loads(result)  # 将字符串转换为json
            try:
                if result['count'] == '0':
                    break
            except Exception as e:
                print('出现异常：', e)

            if result['infocode'] == '10001' or result['infocode'] == '10003':
                # print(result)
                print('无效的密钥！！！！！！！！！！！！！，重新切换密钥进行爬取')
                buffer_keys.remove(buffer_keys[0])
                try:
                    amap_key = buffer_keys[0]  # 总是获取队列中的第一个密钥
                except Exception as e:
                    print('密钥已经用尽，程序退出...')
                    exit(0)
                result = getpoi_page(grids, keywords, i, amap_key)
                result = json.loads(result)
            hand(poilist, result)
        i = i + 1
    return poilist


# 数据写入csv文件中
def write_to_csv(poilist, citycode, classfield, coord,folder_name_full):
    data_csv = {}
    lons, lats, names, addresss, pnames, citynames, business_areas, types, typecodes, ids, type_1s, type_2s, type_3s, type_4s = [], [], [], [], [], [], [], [], [], [], [], [], [], []

    if len(poilist) == 0:
        print("处理完成，当前citycode:" + str(citycode), ", classfield为：", str(classfield) + "，数据为空，，，结束.......")
        return None, None

    for i in range(len(poilist)):
        location = poilist[i].get('location')
        name = poilist[i].get('name')
        address = poilist[i].get('address')
        pname = poilist[i].get('pname')
        cityname = poilist[i].get('cityname')
        business_area = poilist[i].get('business_area')
        type = poilist[i].get('type')
        typecode = poilist[i].get('typecode')
        lng = str(location).split(",")[0]
        lat = str(location).split(",")[1]
        id = poilist[i].get('id')

        if (coord == 2):
            result = gcj02_to_wgs84(float(lng), float(lat))
            lng = result[0]
            lat = result[1]
        if (coord == 3):
            result = gcj02_to_bd09(float(lng), float(lat))
            lng = result[0]
            lat = result[1]
        type_1, type_2, type_3, type_4 = '','','',''
        if str(type) != None and str(type) != '':
            type_strs = type.split(';')
            for i in range(len(type_strs)):
                ty = type_strs[i]
                if i == 0:
                    type_1 = ty
                elif i == 1:
                    type_2 = ty
                elif i == 2:
                    type_3 = ty
                elif i == 3:
                    type_4 = ty

        lons.append(lng)
        lats.append(lat)
        names.append(name)
        addresss.append(address)
        pnames.append(pname)
        citynames.append(cityname)
        if business_area == []:
            business_area = ''
        business_areas.append(business_area)
        types.append(type)
        typecodes.append(typecode)
        ids.append(id)
        type_1s.append(type_1)
        type_2s.append(type_2)
        type_3s.append(type_3)
        type_4s.append(type_4)
    data_csv['lon'], data_csv['lat'], data_csv['name'], data_csv['address'], data_csv['pname'], \
    data_csv['cityname'], data_csv['business_area'], data_csv['type'], data_csv['typecode'], data_csv['id'], data_csv[
        'type1'], data_csv['type2'], data_csv['type3'], data_csv['type4'] = \
        lons, lats, names, addresss, pnames, citynames, business_areas, types, typecodes, ids, type_1s, type_2s, type_3s, type_4s

    df = pd.DataFrame(data_csv)


    if os.path.exists(folder_name_full) is False:
        os.makedirs(folder_name_full)
    file_name = classfield + ".csv"
    file_path = os.path.join(folder_name_full, file_name)
    df.to_csv(file_path, index=False)
    print('写入成功')
    return folder_name_full, file_name


# 将返回的poi数据装入集合返回
def hand(poilist, result):
    # result = json.loads(result)  # 将字符串转换为json
    pois = result['pois']
    for i in range(len(pois)):
        poilist.append(pois[i])


# 单页获取pois
def getpoi_page(grids, types, page, key):
    polygon = str(grids[0]) + "," + str(grids[1]) + "|" + str(grids[2]) + "," + str(grids[3])
    req_url = poi_pology_search_url + "?key=" + key + '&extensions=all&types=' + quote(
        types) + '&polygon=' + polygon + '&offset=25' + '&page=' + str(
        page) + '&output=json'
    print('请求url：', req_url)

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=5))
    s.mount('https://', HTTPAdapter(max_retries=5))
    try:
        data = s.get(req_url, timeout=5)
        return data.text
    except requests.exceptions.RequestException as e:
        data = s.get(req_url, timeout=5)
        return data.text
    return None


def get_drids(min_lng, max_lat, max_lng, min_lat, keyword, key, pology_split_distance, all_grids):
    grids_lib = generate_grids(min_lng, max_lat, max_lng, min_lat, pology_split_distance)

    print('划分后的网格数：', len(grids_lib))
    # print(grids_lib)

    # 3. 根据生成的网格爬取数据，验证网格大小是否合适，如果不合适的话，需要继续切分网格
    for grid in grids_lib:
        one_pology_data = getpoi_page(grid, keyword, 1, key)
        data = json.loads(one_pology_data)
        #print(data)

        while int(data['count']) > 890:
            get_drids(grid[0], grid[1], grid[2], grid[3], keyword, key, pology_split_distance / 2, all_grids)


        all_grids.append(grid)
    return all_grids


def get_data(city, keyword, coord,leftup_lon, leftup_lat, rightdown_lon, rightdown_lat,forder_name_full):

    amap_key = buffer_keys[0]  # 总是获取队列中的第一个密钥
    # 2. 生成网格切片格式：

    grids_lib = generate_grids(leftup_lon, leftup_lat,rightdown_lon, rightdown_lat, pology_split_distance)

    print('划分后的网格数：', len(grids_lib))
    # print(grids_lib)

    all_data = []
    begin_time = time.time()

    print('==========================正式开始爬取啦！！！！！！！！！！！================================')

    for grid in grids_lib:
        # grid格式：[112.23, 23.23, 112.24, 23.22]
        one_pology_data = getpois(grid, keyword)

        print('===================================当前矩形范围：', grid, '总共：',
              str(len(one_pology_data)) + "条数据.............................")

        all_data.extend(one_pology_data)

    end_time = time.time()
    print('全部：', str(len(grids_lib)) + '个矩形范围', '总的', str(len(all_data)), '条数据, 耗时：', str(end_time - begin_time),
          '正在写入CSV文件中')
    file_folder, file_name = write_to_csv(all_data, city, keyword, coord,forder_name_full)

def voxel_filter(point_cloud, leaf_size):
    filtered_points = []
    # 作业3
    # 屏蔽开始
    point_cloud = np.array(point_cloud)
    point_xy = point_cloud[:,:2].astype(np.float)
    point_min = np.min(point_xy,axis=0)
    point_max = point_xy.max(axis=0)
    point_oxy = point_max - point_min
    Dxy = np.floor(point_oxy/leaf_size)  # 计算格网尺寸
    h= list()
    for i in range(len(point_xy)):
        hx = (point_xy[i][0] - point_min[0])//leaf_size
        hy = (point_xy[i][1] - point_min[1])//leaf_size
        h.append(hx + hy*Dxy[0])
    h = np.array(h)
    sort = h.argsort()
    value = h[sort]
    temp = []
    for i, element in enumerate(value):  # 在格网中随机选取一点降采样
        if not element in temp:
            temp.append(element)
            filtered_points.append(point_cloud[sort[i], :])

    return filtered_points

def main(csvname,poipath,outdir,xbegin,xend,ybegin,yend):
    deltax=(xend-xbegin)*0.2
    deltay=(ybegin-yend)*0.2
    print (deltax,deltay)
    # 加载自己的点云文件
    csv_file = os.path.join(poipath,csvname)
    # print (csv_file)
    with open(csv_file,'r',encoding='utf-8') as f:
        reader = csv.reader(f)

        a=list(reader)
        #print (a[1])
        #print (len(a))
        point_cloud=[]
        for i in range(1,len(a)):
            if float(a[i][0])>xbegin and float(a[i][0])<xend:
                if float(a[i][1])>yend and float(a[i][1])<ybegin:
                    #print (a[i])
                    point_cloud.append(a[i])
    print(xbegin,xend,ybegin,yend)


        #print (point_cloud)
    # 调用voxel滤波函数，实现滤波
    filtered_cloud = voxel_filter(point_cloud, 0.01)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    out_path =  os.path.join(outdir,csvname)
    result_file = open(out_path,'w',newline='',encoding='gbk')
    writer=csv.writer(result_file)
    writer.writerow(('x','y','name','address','pname','cityname','business_area','type','typecode','id','type1','type2','type3','type4'))
    for j in filtered_cloud:
        writer.writerow(j)
    result_file.close()


def osmdl(coordinates, cache_path):
    path = cache_path
    if not os.path.exists(path):
        os.mkdir(path)
    lefttop_lat_deg = coordinates[0]
    lefttop_lon_deg = coordinates[1]
    rightbottome_lat_deg = coordinates[2]
    rightbottome_lon_deg = coordinates[3]

    deltax=(rightbottome_lon_deg-lefttop_lon_deg)*0.05
    deltay=(lefttop_lat_deg-rightbottome_lat_deg)*0.05

    north = lefttop_lat_deg-deltay
    south = rightbottome_lat_deg+deltay
    east = rightbottome_lon_deg-deltax
    west = lefttop_lon_deg+deltax

    print('Begin downloading OSM data of' + str((north, south, east, west)))
    G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    if not os.path.exists(os.path.join(path, 'osm')):
        os.makedirs(os.path.join(path, 'osm'))

    ox.io.save_graph_shapefile(G, filepath=os.path.join(path, 'osm/'), encoding='utf-8')
    G_projected = ox.project_graph(G)
    ox.plot_graph(G_projected)

def readtfw(tfwpath,tifpath):
    f=open(tfwpath,'r')
    tfws=f.readlines()
    leftlon=float(tfws[4].rstrip('\n'))
    leftlat=float(tfws[5].rstrip('\n'))
    xres=float(tfws[0].rstrip('\n'))
    yres=float(tfws[3].rstrip('\n'))
    #print (leftlon,leftlat,xres,yres)
    img=cv_imread(tifpath)
    height,width,channels=img.shape
    print (height,width)
    rblon=leftlon+xres*width
    rblat=leftlat+yres*height
    #print (leftlat,leftlon,rblat,rblon)
    return (leftlat,leftlon,rblat,rblon,width,height)

def takejson(getjson):
    json1=json.loads(getjson)
    #coordinates=json1['coord']
    mainpath=json1['mainpath']
    tifpath=json1['tifpath']
    tfwpath=json1['tfwpath']
    tfwname=tfwpath.split('/')[-1]
    outputname=tfwname.replace('.','_marked.')
    coordinates=readtfw(tfwpath,tifpath)[0:4]
    #print (coordinates)
    wnh=readtfw(tfwpath,tifpath)[4:]
    print (wnh)

    while True:
        sha = hashlib.sha256()
        sha.update(str(time.time()).encode('utf-8'))
        cache_folder = 'Cache_{}'.format(sha.hexdigest())
        cache_path = os.path.join(mainpath, cache_folder)

        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
            break

    output=json1['output']
    if not os.path.exists(output):
        os.makedirs(output)
    copyfile(tfwpath,os.path.join(output,outputname))
    print (os.path.join(output,outputname))
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    # 初始化密钥队列
    init_queen()
    folder_name_full=os.path.join(cache_path,'poi')
    if not os.path.exists(folder_name_full):
        os.makedirs(folder_name_full)
    outdir = os.path.join(cache_path, 'poi2')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    leftup_lon, leftup_lat = coordinates[1],coordinates[0]
    rightdown_lon, rightdown_lat = coordinates[3],coordinates[2]
    print (leftup_lat,leftup_lon,rightdown_lat,rightdown_lon)
    shppath=os.path.join(cache_path,'osm','edges.shp')
    poipath=outdir
    callback=json.dumps({'cachepath':cache_path,'tifpath':tifpath,'tfwpath':tfwpath,
        'output':output,'tifname':outputname.replace('tfw','tif'),'wnh':wnh,'coord':coordinates})

    
#    POI类型编码，类型名或者编码都行，具体参见《高德地图POI分类编码表.xlsx》
    typs = ['bus','hospital','shopping','museum','school']  # ['企业', '公园', '广场', '风景名胜', '小学']ust eng

    for types in typs:
        get_data(city_code, types, coord, leftup_lon, leftup_lat, rightdown_lon, rightdown_lat,folder_name_full)

    csvlist=os.listdir(folder_name_full)
    print (csvlist)

    for csvfile in csvlist:
        main(csvfile,folder_name_full,outdir,leftup_lon,rightdown_lon,leftup_lat,rightdown_lat)
    
    osmdl(coordinates,cache_path)

    return callback

if __name__ == '__main__':
    #jsonstring={'coord':[31.341911,121.431875,31.2926472,121.4898827],'mainpath':'.'}
    # jsonstring={'mainpath':'./','tifpath':r'E:\PycharmProject\testmapnik2\tifntfw\shanghairesize.tif','tfwpath':r'E:\PycharmProject\testmapnik2\tifntfw\shanghairesize.tfw','output':'./output'}
    #jsonstring={'mainpath':r'C:\Users\Sweetday\Desktop','tifpath':r'C:\Users\Sweetday\Desktop\EPSG_4326_16\shanghairesize.tif','tfwpath':r'C:\Users\Sweetday\Desktop\EPSG_4326_16\shanghairesize.tfw','output':r'C:\Users\Sweetday\Desktop\output'}
    # json1=json.dumps(jsonstring)
    callback=takejson(sys.argv[1])
    print (callback)

    #readtfw('../../marked/shanghai/map/shanghai.tfw','../../marked/shanghai/map/shanghai.tif')
    #mainpath：缓存文件夹的路径，tifpath：生成地图路径，tfwpath：生成地图tfw路径,output：生成标注地图和对应tfw储存路径
    #callback回传的json给标注脚本用
