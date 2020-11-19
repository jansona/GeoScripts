# yangzhen
# 2020.11.10
import json
import OsmAffinebyMap as oam
import compositingonnum as csn
import shp2raster2 as s2r
import os
import cv2
import numpy as np
import shutil
import argparse
import hashlib
import time


def cv_imread(file_path):
    cv_img=cv2.imdecode(np.fromfile(file_path,dtype=np.uint8),-1)
    return cv_img


def cv_imwrite(filepath,img):
    cv2.imencode(".png",img)[1].tofile(filepath)


def cutbigimage(rmpath,mappath,outraster,outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    img1=cv_imread(rmpath)
    img2=cv_imread(mappath)
    img3=cv_imread(outraster)
    img3=cv2.cvtColor(img3,cv2.COLOR_GRAY2BGR)
    width=img1.shape[1]
    height=img1.shape[0]
    x=0
    n=0
    while x<width:
        y=0
        m=0
        while y<height:
            sample1=[img1[y:y+256,x:x+256],img2[y:y+256,x:x+256],img3[y:y+256,x:x+256]]
            img=np.hstack(sample1)
            cv_imwrite(os.path.join(outdir,str(n)+'_'+str(m)+'.png'),img)
            y=y+256
            m=m+1
        x=x+256
        n=n+1


def takejson(getjson):
    jsonstring1=json.loads(getjson)
    #print (json1)
    sha = hashlib.sha256()
    sha.update(str(time.time()).encode('utf-8'))
    cacheRootPath = os.path.join(jsonstring1['Cachepath'], 'Cache_{}'.format(sha.hexdigest()))
    jsonstring1['Cachepath'] = cacheRootPath

    rmpath,mappath=csn.takejson(json.dumps(jsonstring1))
    shp=jsonstring1['shppath']


    outraster=os.path.join(cacheRootPath,'osm.png')
    #shp2=os.path.join(jsonstring1['Cachepath'],'edges.shp')
    #s2r.chageproj(shp,shp2)
    s2r.shp2raster(mappath,shp,outraster)
    zoom=jsonstring1['remotepath'].split('/')[-2]
    zoomal=jsonstring1['remotepath'].split('/')[-1]
    dirtype=jsonstring1['remotepath'].split('/')[-3]+'_'+jsonstring1['mappath'].split('/')[-3]+'_矢量'
    mainpath='/'.join(jsonstring1['remotepath'].split('/')[:-4])
    outdir=os.path.join(mainpath,dirtype,zoom,zoomal)
    jsonstring = {'inpath1': mappath,
                  'inpath2': outraster,
                  'outpath': outraster.replace('osm','osm2')}
    jsonpath = json.dumps(jsonstring)
    #print (jsonpath)
    oam.OsmAffinebyMap(jsonpath)
    cutbigimage(rmpath, mappath, jsonstring['outpath'], outdir)
    shutil.rmtree(jsonstring1['Cachepath'])
    #cutbigimage(r'F:\Taiwan3\Cache\rm.png',r'F:\Taiwan3\Cache\map.png',r'F:\Taiwan3\Cache\osm2.png',r'F:\Taiwan3\Cache\test')


if __name__=='__main__':
    # jsonstring1={'remotepath':'F:/Taiwan3/metadata/谷歌影像无标注/14/14_14aligned',
    #     'mappath':r'F:/Taiwan3/metadata/谷歌地图无标注/14/14_14aligned',
    #     'shppath':'F:/Taiwan3/OSM/road/edges.shp','Cachepath':'F:/Taiwan3/Cache'}
    # json1=json.dumps(jsonstring1)
    # takejson(json1)
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json', type=str, help='输入json字符串')
    args = parser.parse_args()

    takejson(args.input_json)
