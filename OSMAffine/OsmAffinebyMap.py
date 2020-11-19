# yangzhen
# 2020.11.10


import json
import cv2
import numpy as np
import GetRoadFromMap as grfm
import GetRoadLine as grl
import GetIntersectPoint as gip
import Affine_ICP_Encapsulation as aie


def OsmAffinebyMap(jsonpath):
    """osm数据配准到map"""
    # 获取输入参数（输入文件夹、输出文件夹）---------------------------------------
    jsonstring = json.loads(jsonpath)
    # 输入文件夹
    mappath = jsonstring['inpath1']
    osmpath = jsonstring['inpath2']
    # 输出文件夹
    nosmpath = jsonstring['outpath']
    # 获取输入数据---------------------------------------------------------------
    map = cv2.imread(mappath)
    roadnet_osm = cv2.imread(osmpath, flags=cv2.IMREAD_GRAYSCALE)
    roadnet_osm[roadnet_osm > 0] = 255
    # map中获取面状道路网--------------------------------------------------------
    roadarea_map = grfm.GetRoadFromMap(map)
    # 面状map中获取道路网骨架线---------------------------------------------------
    roadnet_map = grl.GetRoadLine(roadarea_map)
    # 分别获取两种数据的道路网线交叉点---------------------------------------------
    point_map = gip.GetIntersectPoint(roadnet_map)
    point_osm = gip.GetIntersectPoint(roadnet_osm)
    # 利用交叉点进行配准----------------------------------------------------------
    # osm道路网转为点云
    x, y = np.where(roadnet_osm == 255)
    ptcloud_osm = np.vstack((y, x))
    ptcloud_osm = ptcloud_osm.T
    # 开始对OSM配准
    nptcloud_osm = aie.Affine_ICP(point_osm, point_map, ptcloud_osm, 20, 100)
    # 配准后OSM点云转栅格
    rows, cols = roadnet_osm.shape[0:2]
    nroadnet_osm = np.zeros([rows, cols], dtype=np.uint8)
    for i in range(len(nptcloud_osm)):
        if ((0 <= nptcloud_osm[i, 1] and nptcloud_osm[i, 1] < rows) and
            (0 <= nptcloud_osm[i, 0] and nptcloud_osm[i, 0] < cols)):
            nroadnet_osm[int(nptcloud_osm[i, 1]),
                         int(nptcloud_osm[i, 0])] = 255
    # 保存新的OSM数据
    cv2.imwrite(nosmpath, nroadnet_osm)
