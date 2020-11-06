# coding=UTF-8
import mapnik
import xml.dom.minidom
import sys
import json
import os
from shutil import rmtree
import argparse


def alter_xml(getjson):

    jsonstring=json.loads(getjson)#loads将前端传给后端的json字符产解析回字典

    # 以下两个资源文件已被封装到镜像中（或者与脚本同路径也行）
    script_path = os.path.split(os.path.realpath(__file__))[0]
    xml_path = '/{}/template.xml'.format(script_path)#写死，原始的样式xml
    labelpath='/{}/label_png'.format(script_path)#写死的路径，图标素材
    tifname=jsonstring['tifname']
    wnh=jsonstring['wnh']
    output=jsonstring['output']

    cachepath=jsonstring['cachepath']
    mod_xml = os.path.join(cachepath,'new.xml')

    osm_path = os.path.join(cachepath,'osm','edges.shp')
    poipath=os.path.join(cachepath,'poi2')
    ditu_path = jsonstring['tifpath']
    bus_path= os.path.join(poipath,'bus.csv')
    shop_path = os.path.join(poipath,'shopping.csv')
    museum_path = os.path.join(poipath,'museum.csv')
    school_path  = os.path.join(poipath,'school.csv')
    hospital_path = os.path.join(poipath,'hospital.csv')

# 需要修改的xml位置
# xml_path = 'C:/Users/CSU/Desktop/ceshi_xml/shanghai.xml'
# # 修改后的xml位置
# stylesheet = 'D:/train/zhuji/newyork/change.xml'

# 修改的地理数据
# ditu_path = r'd:\train\zhuji\newyork\map\ditu.tif'
# osm_path = r'd:\train\zhuji\newyork\street\osm_lines.shp'
# bus_path = r'd:\train\zhuji\newyork\poi\busstation.csv'
# shop_path = r'd:\train\zhuji\newyork\poi\shopping.csv'
# museum_path = r'd:\train\zhuji\shanghai\poi\museum.csv'
# school_path = r'd:\train\zhuji\shanghai\poi\school.csv'
# hospital_path = r'd:\train\cnshanghai\shanghai\poi\hospital.csv'


    dom = xml.dom.minidom.parse(xml_path)
    root = dom.documentElement
    # 改变地图路径
    layer = root.getElementsByTagName('Layer')
    x0 = layer[0].getElementsByTagName("Datasource")[0]
    y0 = x0.getElementsByTagName("Parameter")[0].childNodes[0]
    y0.data = ditu_path
    # 改变shop路径
    x1 = layer[1].getElementsByTagName("Datasource")[0]
    y1 = x1.getElementsByTagName("Parameter")[0].childNodes[0]
    y1.data = shop_path
    # 改变bus路径
    x2 = layer[2].getElementsByTagName("Datasource")[0]
    y2 = x2.getElementsByTagName("Parameter")[0].childNodes[0]
    y2.data = bus_path
    # 改变hospital路径
    x3 = layer[3].getElementsByTagName("Datasource")[0]
    y3 = x3.getElementsByTagName("Parameter")[0].childNodes[0]
    y3.data = hospital_path
    # 改变museum路径
    x4 = layer[4].getElementsByTagName("Datasource")[0]
    y4 = x4.getElementsByTagName("Parameter")[0].childNodes[0]
    y4.data = museum_path
    # 改变school路径
    x5 = layer[5].getElementsByTagName("Datasource")[0]
    y5 = x5.getElementsByTagName("Parameter")[0].childNodes[0]
    y5.data = school_path
    # 改变osm路径
    x6 = layer[6].getElementsByTagName("Datasource")[0]
    y6 = x6.getElementsByTagName("Parameter")[0].childNodes[0]
    y6.data = osm_path
    style=root.getElementsByTagName('Style')
    z1 =style[2].getElementsByTagName("Rule")[0]
    z1=z1.getElementsByTagName("MarkersSymbolizer")[0]
    z1.setAttribute("file",os.path.join(labelpath,'shopping.png'))
    z2 = style[3].getElementsByTagName("Rule")[0]
    z2 = z2.getElementsByTagName("MarkersSymbolizer")[0]
    z2.setAttribute("file", os.path.join(labelpath, 'bus_station1.png'))
    z3 = style[5].getElementsByTagName("Rule")[0]
    z3 = z3.getElementsByTagName("MarkersSymbolizer")[0]
    z3.setAttribute("file", os.path.join(labelpath, 'hospital.png'))
    z4 = style[7].getElementsByTagName("Rule")[0]
    z4 = z4.getElementsByTagName("MarkersSymbolizer")[0]
    z4.setAttribute("file", os.path.join(labelpath, 'mum1.png'))
    z5 = style[9].getElementsByTagName("Rule")[0]
    z5 = z5.getElementsByTagName("MarkersSymbolizer")[0]
    z5.setAttribute("file", os.path.join(labelpath, 'school.png'))


    # 将修改后的xml文件保存
    with open(mod_xml,'w') as fh:
        dom.writexml(fh)
        print('写入XML OK!')

    tifpath=os.path.join(output,tifname)
    print (tifpath)

    map = mapnik.Map(wnh[0],wnh[1])
    mapnik.load_map(map,str(mod_xml))
    map.zoom_all()
    mapnik.render_to_file(map,str(tifpath))

    rmtree(str(cachepath))

if __name__ =='__main__':

    # json_dict = {"cachepath":"/temp/Cache_5cefba8feb8e1d323805bc79437e595ede17bb420e3e9a7c80a15d863d4793fe",
    # "tifpath":"/temp/shanghai.tif","tfwpath":"/temp/shanghai.tfw","output":"/temp/output",
    # "tifname":"shanghai_marked.tif","wnh":[5376,5376],"status":"Finish"}
    # json_str = json.dumps(json_dict)
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--input_json', type=str, help='输入json字符串')
    # args = parser.parse_args()
    # print(args)
    print(sys.argv[1])
    sys.argv[1] = sys.argv[1].replace("'", '"')
    alter_xml(sys.argv[1])
    #这边的json直接接收poidownload的callback