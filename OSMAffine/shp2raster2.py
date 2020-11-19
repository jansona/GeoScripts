# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 14:48:44 2020

@author: CSUZHANG01
"""
# -*- coding: utf-8 -*-
import os
import numpy as np
import gdal
from osgeo import ogr
from osgeo import osr

def chageproj(src_file,dst_file):
    src_ds = ogr.Open(src_file)
    src_layer = src_ds.GetLayerByIndex(0)
    src_srs = src_layer.GetSpatialRef()  # 输入数据投影

    # 输出数据投影定义，参考资料：http://spatialreference.org/ref/sr-org/8657
    srs_def = """+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over """
    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromProj4(srs_def)

    # 创建转换对象
    ctx = osr.CoordinateTransformation(src_srs, dst_srs)

    # 创建输出文件
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = driver.CreateDataSource(dst_file)
    dst_layer = dst_ds.CreateLayer('province', dst_srs, ogr.wkbLineString)

    # 给输出文件图层添加属性定义
    layer_def = src_layer.GetLayerDefn()
    for i in range(layer_def.GetFieldCount()):
        field_def = layer_def.GetFieldDefn(i)
        dst_layer.CreateField(field_def)

    # 循环遍历源Shapefile中的几何体添加到目标文件中
    src_feature = src_layer.GetNextFeature()
    while src_feature:
        geometry = src_feature.GetGeometryRef()
        #print (geometry)
        geometry.Transform(ctx)
        dst_feature = ogr.Feature(layer_def)
        dst_feature.SetGeometry(geometry)  # 设置Geometry
        # 依次设置属性值
        for i in range(layer_def.GetFieldCount()):
            field_def = layer_def.GetFieldDefn(i)
            field_name = field_def.GetName()
            dst_feature.SetField(field_name, src_feature.GetField(field_name))
        dst_layer.CreateFeature(dst_feature)
        dst_feature = None
        src_feature = None
        src_feature = src_layer.GetNextFeature()
    dst_ds.FlushCache()

    del src_ds
    del dst_ds

    # 创建Shapefile的prj投影文件
    dst_srs.MorphToESRI()
    (dst_path, dst_name) = os.path.split(dst_file)
    with open(dst_path + os.pathsep + dst_name + '.prj', 'w') as f:
        f.write(dst_srs.ExportToWkt())

def shp2raster(imagefile,line_file,outraster_file):
    field_name="FID"
    ds = ogr.Open(line_file, 1)
    #print (ds)
    oLayer = ds.GetLayerByIndex(0)
    prosrs = oLayer.GetSpatialRef()
    print (prosrs)
    #print(oLayer.GetGeomType())  #矢量类型，输出的是1,2,3（点、线、面）
    oDefn = oLayer.GetLayerDefn()

    #这里可以不管，这部分是获取字段的名称，遍历名称以及他们的属性的
    iFieldCount = oDefn.GetFieldCount()
    for iAttr in range(iFieldCount):
        oField =oDefn.GetFieldDefn(iAttr)
        #print(oField.GetNameRef())
    # oField.GetFieldTypeName(oField.GetType()),
    # oField.GetWidth(),
    # oField.GetPrecision())

    #这里是创建字段的过程，这里是一个一个创建的，直接全部创建的没时间找，你们看到了麻烦评论告诉我下
    oFieldID =ogr.FieldDefn(field_name, ogr.OFTInteger)
    oLayer.CreateField(oFieldID, 1)
    fieldIndex0 = oDefn.GetFieldIndex(field_name)
    for i in range(0,oLayer.GetFeatureCount()):
        feature = oLayer.GetFeature(i)
        value= 1  #创建的每个值都等于1
        feature.SetField(fieldIndex0,value)
        oLayer.SetFeature(feature)
    feature.Destroy()
    ds.Destroy()

    image = gdal.Open(imagefile)

    width = image.RasterXSize
    height = image.RasterYSize
    #geotransform=image.GetGeoTransform()
    #ref=image.GetProjection()
    opt={'format':"GTiff",'width':width,'height':height,'initValues':0,'attribute':field_name}
    gdal.Rasterize(outraster_file,line_file,**opt)
    print("success")

    img = gdal.Open(outraster_file)
    #print (img)
    #print (np.shape(img))
    data=img.GetRasterBand(1).ReadAsArray().astype(np.uint8)


    data[np.where(data>0)]=255
    #print (data)
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outraster_file,width,height,1,gdal.GDT_Byte)
    ds.GetRasterBand(1).WriteArray(data)
    ds=None
    print (outraster_file + '  success')
'''
if __name__=='__main__':
    imagefile = "D:/BMDownload/Rect#1_卫图/Rect#1_卫图_Level_17.tif"  # 参考图像，里面有坐标系需要用到
    # line_file = "./../poi/Cache/osm/edges.shp"  #需要转的矢量数据
    # line_file="./water/water.shp"
    line_file = './road/edges.shp'
    outraster_file = "./test.tif"  # 存储的结果
    shp2raster(imagefile, line_file, outraster_file)
'''